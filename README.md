# Cerberus Home Security System
A Raspberry Pi 4-based home security system that combines GPIO-connected door sensors, automated video recording, persistent event logging, and Telegram notifications. The system uses a modular software architecture with independent processes for sensor monitoring, arming/disarming, and camera control. 
This project is suitable for small-scale security systems, and was originally implemented for an apartment unit. And yes, Cerberus is named after the guard dog of the Underworld. 

## Features
**GPIO-based Intrusion Detection**: Monitors connected door sensors for opening events.

**Arm/Disarm Control**: Uses a physical button connected to the Pi's GPIO pins to enable or disable security monitoring. 

**Event-Triggered Recording**: Automatically records a video when a door-opening event is detected while the system is armed. 

**Automated Event Storage**: Saves security recordings and maintains logs of relevant system and security events. 

**Remote Notifications**: Integrates with the Telegram Bot API to send security alerts to a mobile device in real time. 

**Modular Architecture**: Separates sensor monitoring, arming/disarming, and camera recording into independent programs. 

**Linux Service Management**: Uses systemd to run selected components as background services. 

**Failure Handling**: Implements network failure and timeout handling for more robust operation.

## Event Workflow
1. The user can choose to arm or disarm the security system using the physical button. 
2. The door sensor program detects a door-opening event. 
3. If the system is armed, the event triggers the camera-recording workflow, triggers a Telegram notification to be sent, and logs everything. 
4. If the system is disarmed, the event is logged. 

## Hardware used
- Raspberry Pi 4
- [NC Magenetic Reed Switch Sensors](https://www.amazon.com/Alarm-Magnetic-Reed-Switch-Security/dp/B0G6WRNK4Q/ref=sr_1_17_sspa?crid=2EZRWT3PLGX4&dib=eyJ2IjoiMSJ9.gC8-dvUcHJusgqm9T5JfmBOU09LVHHM7Y4_zARvZF-q8-emfZB_tc_4nCOzqFMgt-dnChoVYhrjEIl_phe_fznzTpj9i6gfq90oMOQtLvmScP3sz-8_3a3XwV9CQkpMcxEbB8XLKesxdpPm7MriN1hZrsFtWvZloRCI2mWcs0Qa_JCjeLHQy38yjMozxSxDDEaotvPLlq0joiQnEaWy8pg-Q7Vo7r3zA_s8lfdie5YM.adPT_fMhCamJa1VUmXx0xpb2aBmUcRmlAyEsz1U1nb4&dib_tag=se&keywords=nc+magnetic+reed+switch&qid=1792969798&sprefix=nc+magenetic+reed+switc%2Caps%2C147&sr=8-17-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9tdGY&psc=1)
- [Breadboard kit](https://www.amazon.com/BOJACK-Electronics-Potentiometer-tie-Points-Breadboard/dp/B099MQV8ZW/ref=sr_1_2_sspa?crid=25TDUBWNCDS2S&dib=eyJ2IjoiMSJ9.Bwc7T27OfBQJVVly01otvL2m2jKRP027hIlq1jpB4UYBuVSL4F_z7WaJjGl2BTQ23UcMZEUPfrbQ8FJNxIbVc-xxCvZhTST_oxuWQmsb3NO8Upqqk_YhedSGx8gvn4rlbX5QBJ5pjFC_zuQ4dPkV_VLOdjEwMkEa_gOULlavvYPXWAK4llKoTomovhCJt2IqovMFg0c5r8gq4orZ3baRbmh27iwZZ8T8IJmNyHOK1tY.sC-YlXK3v9WhYZvWJQodPClzufaX-IgLbcQkELFTHhY&dib_tag=se&keywords=breadboard+kit&qid=1792970780&sprefix=breadboard+ki%2Caps%2C237&sr=8-2-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&psc=1)
- [Additional jumper wire](https://www.amazon.com/TUOFENG-Solid-Colors-Tinned-Copper/dp/B07TX6BX47/ref=sr_1_4?dib=eyJ2IjoiMSJ9.wbnPImhnx-oKJ9Uji83YnXMqhS1xuvrYja3dPoXe9JqwMH0zKU4luIwrQnuCYIsJPgRhtvQJvmJJrc7oiISsABF1rpZZ-auQ8NvSIHti-6mq1novOuOh5aiPBui0CTAYZrNt6bQLRYF_80hlXJGrtZd628RUG-UM8qXXYJD6f07WCVGX_2jqUYbaSUnDtSHEA5LbhPb33QWV3D1dC2y3zGF5bD-tioSKqTmZTbuUD1Q.dBbTATicFj62QftE1FI_Z7PdQ_555wzNIjOcerVfeRc&dib_tag=se&keywords=pcb+jumper+wire&qid=1792971017&sr=8-4)
- [Raspberry Pi Camera Module](https://www.amazon.com/Arducam-Raspberry-Camera-Module-1080P/dp/B07RWCGX5K/ref=sr_1_1?crid=1M0XPGM02ZF3J&dib=eyJ2IjoiMSJ9.uf64hZIk7fZT-s5oIshEmb9-lV2y-eYr5AAkbxoBHyFz7bQOE55PH-jHwqI_uUROKzGwSMYfugybszIx0uRXTZyogfQ0BXNrnz-VqjY-7HhKdM5AMFo0xTicng2WpWAKuP9mNX6rDYBvAVYC7O3RK6rfRI4Tclxth1ffeLUYMs-Bs4-pfAyNn6HFmJ97r6zThPO78Q2DD5P-v5WsNcEyg0yaQ24ZcabSNpaCQkzNSrk.P4LSTfek1lAnqkvfHYwh4of1uNNfiaRLZw7OTDNLHPs&dib_tag=se&keywords=raspberry+pi+4+camera+module+with+case&qid=1792970824&sprefix=rasspberry+pi+4+camera+module+with+ca%2Caps%2C227&sr=8-1)
- Raspberry Pi compatible USB microphone
- Power supply and storage for the Raspberry Pi

The breadboard kit as a whole isn't necessary - components used for it for this project were jumper wires, the breadboard itself, and the physical button. Additional jumper wire was purchased to connect the door sensors to the breadboard, and a wire stripper was needed to strip the wire. 

## GPIO Connections 
Sensor > breadboard > GPIO pin 17

Button > breadboard > GPIO pin 27

## Software and Technologies used
- Operating System: Raspberry Pi OS/Debian 13 Trixie
- Hardware interface: GPIO
- Process Management: systemd
- Notifications: Telegram Bot API
- Programming Language: Python 3.13.5
- Camera Interface: rpicam v1.13.0

## Installation and Configuration
### Prerequisites:
- A Raspberry Pi 4 running a compatible Linux distribution. 
- Python3 (comes pre-installed on Raspberry Pi 4, verify your version with "python --version" not including quotes). 
- Hardware listed above, mainly Raspberry Pi 4, door sensors, jumper wire, solderless breadboard, physical button, power supply and storage for the Pi, and the camera module. 
- A Telegram bot and its token. Sensitive credentials are not included in the repository, so ensure you set the following variables before running the notification scripts: 
    - TELEGRAM_BOT_TOKEN - Telegram bot API token
    - TELEGRAM_CHAT_ID - Telegram chat ID that receives security alerts
- See .env.example for the required configuration variables.
### Setup:
1. Clone the repository:
    ```bash
       git clone <repo-url>
       cd cerberus-security-system
    ```
3. Configure GPIO pin assignments, recording location, and logging location as necessary. 
4. Configure Telegram notifications and the token as a local configuration file. 
5. Configure systemd service files. 
6. Enable and start the configured services
    ```bash
        sudo systemctl enable --now <service-name>
    ```
- Replace <service-name> with the actual service name, and repeat for any additional services that should start automatically. 

## Service Management
These commands are helpful for managing background services:
- Inspect the status of a configured service
    ```bash
        systemctl status <service-name>
    ```
- View service logs
    ```bash
        journalctl -u <service-name>
    ```
- View service logs in real time
    ```bash
        journalctl -u <service-name> -f
    ```

## Some Considerations
- Network failures: Network errors should be handled without disrupting local monitoring. 
- Credentials: Keep Telegram bot tokens out of source control and store them securely. 
- Event logging: Logs are handy when troubleshooting issues, and they provide a thorough log of system activity. 
- Service management: systemd files are used to run background services; research using systemd services on a Raspberry Pi to have scripts run at restart. 

## Limitations
This is a personal project where I explored how to use code to interact with hardware. The project currently doesn't have backups or a deletion policy for recordings - that is currently in progress, as it took almost 20 minutes to upload one 30 second recording to Google Drive. 
While this is not a certified security system, it is a great place to start for programmers that are new to the world integrating code with microcontrollers. 

## Improvements
### Areas that will be improved upon/added:
- Arm/disarm indicator light
- Improving recording latency (audio recording sometimes lags behind video)
- Cloud-based backups
- Deletion policy for local backups
- Gesture recognition (mediapipe)
- Web dashboard for monitoring system/events
