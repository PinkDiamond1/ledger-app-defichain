
import fs from 'fs';
import path from 'path';
import process from 'process';

import { ChildProcessWithoutNullStreams, spawn } from "child_process";

import SpeculosTransport from "@ledgerhq/hw-transport-node-speculos-http";

import type { SpeculosHttpTransportOpts } from "@ledgerhq/hw-transport-node-speculos-http";

import { listen } from "@ledgerhq/logs";
import type { Log } from "@ledgerhq/logs";


import { AppClient } from ".."

jest.setTimeout(10000);


/*
This currently does not work if the app is compiled with DEBUG=1; this seems to be inherited from the fact that
@ledgerhq/hw-transport-node-speculos-http seems to be malfunctioning in that case.

The LOG_SPECULOS and LOG_APDUS environment variables can be used to log, respectively, the output of the speculos
process and all the APDUs exchanged during the tests.
*/


const repoRootPath = path.resolve(process.cwd(), '..')

const speculos_path = process.env.SPECULOS || "speculos.py";
const speculos_directory = process.env.SPECULOS_DIR || "./";

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

async function openSpeculosAndWait(opts: SpeculosHttpTransportOpts = {}): Promise<SpeculosTransport> {
  for (let i = 0; ; i++) {
    try {
      return await SpeculosTransport.open(opts);
    } catch (e) {
      if (i > 50) {
        throw e;
      }
    }
    await sleep(100);
  }
}

// Convenience method to send the kill signal and wait for the process to completely terminate
async function killProcess(proc: ChildProcessWithoutNullStreams, signal: NodeJS.Signals = 'SIGTERM', timeout = 10000) {
  return new Promise<void>((resolve, reject) => {
    const pid = proc.pid;
    process.kill(pid, signal);
    let count = 0;
    const intervalHandler = setInterval(() => {
      try {
        process.kill(pid, signal);
      } catch (e) {
        clearInterval(intervalHandler);
        resolve();
      }
      if ((count += 100) > timeout) {
        clearInterval(intervalHandler);
        reject(new Error("Timeout process kill"))
      }
    }, 100)
  });
}

// Sets the speculos automation file using the REST api.
// TODO: It would be better to add this in SpeculosTransport, or create a new custom class.
async function setSpeculosAutomation(transport: SpeculosTransport, automationObj: any): Promise<void> {
  return new Promise((resolve, reject) => {
    transport.instance
      .post(`/automation`, automationObj)
      .then((response) => {
        resolve(response.data);
      }, reject);
  });
}


describe("test AppClient", () => {
  let sp: ChildProcessWithoutNullStreams;
  let transport: SpeculosTransport;
  let app: AppClient;

  beforeAll(async () => {
    if (process.env.LOG_APDUS) {
      listen((arg: Log) => {
        if (arg.type == 'apdu') {
          console.log("apdu:", arg.message);
        }
      });
    }
  });

  beforeEach(async () => {
    sp = spawn(speculos_path, [
      repoRootPath + "/bin/app.elf",
      '-k', '2.1',
      '--display', 'headless'
    ],
      {
        cwd: speculos_directory
      });

    sp.stdout.on('data', function (data) {
      if (process.env.LOG_SPECULOS) {
        console.log('stdout: ' + data);
      }
    });

    sp.stderr.on('data', function (data) {
      if (process.env.LOG_SPECULOS) {
        console.log('stderr: ' + data);
      }
    });

    transport = await openSpeculosAndWait();
    app = new AppClient(transport);
  });

  afterEach(async () => {
    await transport.close();
    await killProcess(sp);
  });


  it("can retrieve the master fingerprint", async () => {
    const result = await app.getMasterFingerprint();
    expect(result).toEqual("1fedcf9d");
  });

  it("can get an extended pubkey", async () => {
    const result = await app.getExtendedPubkey("m/49'/1'/1'/1/3", false);

    expect(result).toEqual("tpubDGxD6st7AMzj6YGzCYzscMw3Rkbwfbgqujm7sqGFgD2Y633QDsNSYUH147LpqCBkn98oTdy6BR2UqH6SDfigDC2qFJVr1cka8CM7Ahvj4nG")
  });

  it("can sign a message", async () => {
    const msg = "The root problem with conventional currency is all the trust that's required to make it work. The central bank must be trusted not to debase the currency, but the history of fiat currencies is full of breaches of that trust. Banks must be trusted to hold our money and transfer it electronically, but they lend it out in waves of credit bubbles with barely a fraction in reserve. We have to trust them with our privacy, trust them not to let identity thieves drain our accounts. Their massive overhead costs make micropayments impossible.";
    const path = "m/84'/1'/0'/0/8";

    const automation = JSON.parse(fs.readFileSync('src/__tests__/automations/sign_message_accept.json').toString());
    await setSpeculosAutomation(transport, automation);

    const result = await app.signMessage(Buffer.from(msg, "ascii"), path)
    expect(result).toEqual("H/UdRAW0qG199HMeweMYFFOgS7ggmNNqwV7HHTYhq6YLb6EiLHJNmBIy0hz06l3GFqxXgNGkk9EU6/Wlpt/RhfU=");
  });
});