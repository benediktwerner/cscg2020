using UnityEngine;
using System;
using System.Net.Sockets;
using System.Text.Encoding;
using System.Security.Cryptography;

class ServerManager : MonoBehavior {
    void Login() {
        this.loggedIn = 0;
        this.start_server_time = -1;
        this.enable_movement = 256;
        this.loginAttempt = Time.get_time();
        this.blocking_position_updates = 1;
        this.black_screen_active = 1;
        this.emojibar_active = 0;
        this.t_fps_text = 0i64;
        this.t_error_text = 0i64;
        this.lastServerPacket = -1.0;
        this.lastHeartbeat = 0.0;
        this.lastUpdate = 0.0;
        var min_port = PlayerPrefs.GetInt("server_min_port", 1337);
        var max_port = PlayerPrefs.GetInt("server_max_port", 1342);
        this.port = this.rand.Next(min_port, max_port);
        this.host = PlayePrefs.GetString("game_host", "maze.liveoverflow.com");
        this.username = PlayerPrefs.GetString("username", "LiveOverflow");
        this.t_server_text = "Login attempt" + this.host + ":" + this.port;
        this.client = new UdpClient(AddressFamily.InterNetwork);
        this.client.Connect(this.host, this.port);

        if (this.threadRecv != null) {
            this.recvLoop = 0;
            this.threadRecv.Abort();
        }

        this.threadRecv = new Thread(this.RecieveDataThread);
        this.threadRecv.isBackground = true;
        this.threadRecv.Start();
        
        StartCorutine(this.LoginLoop);
        StartCorutine(this.consumePlayerQueue);
        StartCorutine(this.consumeEventQueue);
    }

    IEnumerator LoginLoop() {
        if (!this.loggedIn) {
            this.usersecret = new byte[8];
            var userpassword = PlayerPrefs.GetString("userpassword", "xxxxx");
            var hash = SHA256.Create().ComputeHash(ASCII.GetBytes(userpassword))
            Buffer.BlockCopy(hash, 0, this.usersecret, 0, 8);

            var login_pkt = new byte[42];
            login_pkt[0] = 76;
            Buffer.BlockCopy(this.usersecret, 0, login_pkt, 1, this.usersecret.Length);
            login_pkt[9] = (byte) this.username.Length;
            Buffer.BlockCopy(ASCII.GetBytes(this.username), 0, login_pkt, 10, this.username.Length);
            this.sendData(login_pkt);

            yield return new WaitForSeconds(2.0);
        }
    }

    bool sendData(byte[] pkt) {
        var byte_array = new byte[pkt.Length + 2];
        var rand = this.rand.Next(1, 255);
        byte_array[0] = rand;
        byte_array[1] = this.rand.Next(1, 255);
        i = 0;
        for (var i = 0; i < pkt.Length; i++) {
            byte_array[i + 2] = rand ^ pkt[i];
            rand = (byte_array[1] + rand) % 0xFF;
        }
        this.client.Send(byte_array, byte_array.Length);
        return true;
    }
}
