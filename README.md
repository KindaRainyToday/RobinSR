# RobinSR (Python)
~ Why am I doing this?

## Disclaimer
> **This project was made for shit and giggles.**
> Feel free to open an issue if you find bugs (that aren't listed in the Known Issues section) though.

Anyways,
- **I bear no liability** for any consequences resulting from using this.
- This project is **open-source**. Do whatever you want. Just assume it's using the same license as the one in `kcp/__init__.py`, I don't care.

## Features
***EVERYTHING*** in Amizing25's RobinSR.

Do check **Known Issues & Limitations** section if you're curious about some details.

Other than that, it's deadass just a near 1:1 translation to Python. ***Deadass.*** See, I even said it twice.

## Getting Started
### 1. Clone the Repository

```bash
git clone https://github.com/KindaRainyToday/RobinSR
cd RobinSR
```

### 2. Run the Server

Ensure you have `Python 3.12` (or higher) and `pip`

```bash
pip install -r requirements.txt
python -m gameserver
python -m sdkserver
```

### 3. Traffic Forwarding

[FireflySR.Tool.Proxy](https://git.xeondev.com/YYHEggEgg/FireflySR.Tool.Proxy/archive/v2.0.0.zip)

## ~~Frequently~~ Never Asked Questions
### 1. Why are the namings inconsistent (eg: 'req' sometimes is 'body', 'player' is 'json')?
Because I just copied the original RobinSR. I also stole the protos and stuff from NeonSR. Oh right, if you're whoever made NeonSR, do check my `gameserver.net`. I improved it somewhat.

### 2. Why aren't `session.send()` and `session.send_raw()` asynchronous?
Because the `DatagramTransport.sendto()` is already nonblocking without async.

### 3. Why is the `PlayerSession.on_message()` and dummy handling so sexy, considering Python's lack of macros?
Because I am a Python God. 

## Known Issues & Limitations
- Session doesn't get cleaned up if the client doesn't send the logout packet.

    This can easily be band-aid fixed by adding a timeout. But since it's just a singleplayer server, just close the server, lol.

- Certain exceptions in gameserver can stop it from receiving packets. You need to restart the server when that happens.

- Simulated Universe battle isn't implemented. I've only tested with MoC but PF and AS should work just fine.

- Sending chats doesn't update the chat list. Commands still work properly though. Not really an issue unless you a have mental disorder called OCD. If you do, stay the fuck away from Python, go Rust.

- Map keeps on loading forever.

    ...Well I don't give a shit. Feel free to open an issue/PR if you figure out where I fucked it up though.

- Gacha doesn't work properly. My opinion is the same as the one regarding the previous point.

- SceneCastSkill (using techniques) is pretty fucked, especially Castorice. Just enable techniques through srtools website instead of using it ingame.

- The srtools-data file doesn't autoreload when it gets modified. However, entering battle (or using a command) will reload it.

## Acknowledgements
- Xeon, for the original RobinSR
- Amizing25, for the glorious fork. 

    I wonder, is it even still a fork?
    
    So many things were changed and replaced, but the name stays the same.
    
    I guess this is the *Ship of Theseus* of private servers.

- Mero, for the kcp library

- NeonSR, for the protos and some stuff I forgot about
