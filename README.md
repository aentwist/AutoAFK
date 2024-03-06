# AutoAFK
AutoAFK is a tool to automate AFK Arena tasks via ADB using Python, OpenCV and scrcpy. The bot uses image recognition with fuzzy matching, as well as single pixel recognition to automate actions. All actions are done through ADB which means the window does not need to be in focus (you don't even need a monitor attached) and you can continue to use your computer as normal while it runs.

While the bot is designed for AFK Arena the core logic will work for any Android program on an ABD enabled device.

![image](https://github.com/Fortigate/AutoAFK/assets/46250387/ba5608ae-d78f-4345-be6c-f8f7b2867de6)

# How do I run it?
Configure your device so that:
* ADB is enabled
* Resolution is 1920x1080 (other 16:9 resolutions are technically supported but may cause issues)
* AFK's in-game language is set to English (I'd love to support other languages but all image files are taken from the English version)
