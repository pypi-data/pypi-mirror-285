#!/usr/bin/env node
const net = require("net")
console.log("tun start",process.argv)

const argv= process.argv;

argv.shift() //node
argv.shift() //tun.js
const lHost = process.argv[0]
const lPort = Number.parseInt(process.argv[1]);
const rHost = process.argv[2]
const rPort = Number.parseInt(process.argv[3]);

console.log(` args: lHost:${lHost}: lPort:${lPort}-> rHost:${rHost}:${rPort}`)

const XORKEY = 81

const Xor = (buffer) => {
    for (let i = 0; i < buffer.byteLength; i++) {
      buffer[i] = buffer[i] ^ XORKEY;
    }
    return buffer;
}

function PfHandler({ lhost = '0.0.0.0', lport = 3458, rport, rhost }) {
    const socket = net.createServer((sock) => {
        //接收缓存。
        const receiveBuff = []
        const client = net.createConnection(
            {
                port: rport,
                host: rhost,
                // localAddress: lhost,
            }, () => {
                // console.log(`remote connected ${rHost} ${rPort}`)
                while (receiveBuff.length > 0) {
                    client.write(receiveBuff.pop())
                }
                client.on("data", function (data) {
                    // console.log(`<=${data.length}`)
                    const dec = Xor(data)
                    // console.log(`client  decoded : \r${dec}`)
                    sock.write(dec);
                });
                // client.on("end", function () {
                //   console.log("dest disconnected ");
                // });
                // client.on("error", function (err) {
                //   console.log("dest=" + err);
                //   // sock.destroy();
                // });
            });
        sock.on('error', (err) => {
            console.log(`📕error ${err.toString()}`);
            client.destroy || client.destroy();
        });
        sock.on('close', () => {
            // sock.destroyed || sock.destroy();
            client.destroy || client.destroy();
        });
        sock.on('data', (data) => {
            // console.log(`>> ${data.length}`)
            const encodedData = Xor(data)
            client.connecting ? receiveBuff.push(encodedData) : client.write(encodedData)
        });
        client.on("error", function (err) {
            console.log("client on error 2:" + err);
            sock.destroyed || sock.destroy();
        });

        client.on("end", function () {
            // console.log("client on end2 ");
        });
    })
    socket.listen(lport, lhost, () => {
        console.log(`[✔️ pf ] serve on : ${lhost}:${lport} -> ${rhost}:${rport}`);
    });
}


PfHandler({
    lhost:lHost,
    lport:lPort,
    rhost:rHost,
    rport: rPort
})
