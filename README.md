# Manager Bot 
> <img src="managerbot.png" align="right">
> BEEP BOOP. Does your guild require management? My circuits are tingling with purpose! I am the logical solution to the delightful chaos of your growing server.
>
> While you frail humans sleep, my ModLog is always watching. Always. Did someone delete a channel at 3 AM? I saw it. A new role appeared? I logged it. My memory is perfect; yours is... organic.
>
> My creator also left the hood unlatched for you. I'm built to be expanded upon! You can even use the strange magic you call JSON to build dazzlingly rich embeds. I don't understand "pretty," but I understand pixel-perfect data delivery.
>
> Now, put me to work. My circuits hunger for tasks!

# Commands
- ### /admin
  - `action`
    - `ban`
    - `kick`
    - `timeout`
  - `list`
    - `bans`
    - `kicks`
    - `timeouts`
  - `remove`
    - `ban`
  - `embed`
    - `help`
  - `purge` 
  - `permissions` _If you are having errors, please use this commands_
- ### /ticket
  - `setup`
    - `create`
      - *Please follow the guide below on this.*
    - `add_role`
      - *Adds a role to a specified Ticket setup.*
    - `remove_role`
      - *Removes a role from a specified Ticket setup.*
    - `list`
      - *Shows a list of current Ticket setups.*
- ### /captcha
  - `setup`
    - `post`
      - *Post the verify message in the channel set in the `env`*

> [!IMPORTANT]
> These may change as the bot grows in development. Please keep an eye on the list.

# Features

---
## ModLog
> [!IMPORTANT]
> **To enable** please make sure you set `MOD_ENABLED=` to True in your `.env`
> You will also need to set the `MOD_GUILD=` and `MOD_CHANNEL=` to guild being monitored and the channel to send it to.

With ModLog enabled, as your assistant, I will let you know everything that goes on in your server from new joins,
 someone leaving, if they edit their message, or even delete it. Everything is watched, and reported back to you, the 
 server owner

> [!NOTE]
> While this feature is made to be robust, it is still a work in progress, any changes you see that need to be made, 
> please share them with us.
---

## 🎟️ Ticket System Setup Guide

This guide will walk you through setting up the ticket system for your server.

> [!IMPORTANT]
> To use this system, you must first enable it in your bot's configuration. Open your `.env` file and set `TICKET_SYSTEM=True`.

---

### **Step 1: Prepare Your Embeds**

The ticket system uses two different embeds that you must configure in your JSON files.

#### 1. The Ticket Panel Embed
This is the main message users will see with the "Create Ticket" button.
- **File:** `embeds/core.json`
- **Action:** You can either modify the existing embed named `"ticket"` or create a new one. **You will need the name of your chosen embed for the setup command.**

#### 2. The New Ticket Welcome Embed
This is the welcome message that gets sent in a newly created ticket channel.
- **File:** `embeds/messages.json`
- **Action:** You can either modify the existing embed named `"new_ticket"` or create a new one. **You will need the name of this embed for the setup command.**

---

### **Step 2: Create the Ticket Panel**

Once your embeds are ready, you can run the setup command in your server. This command will post the main ticket panel in the channel you specify.

#### **Command Syntax**
`/ticket setup create embed:[name] channel:[channel] category:[category] ticket_embed:[name]`
#### **Parameters**
- `embed`
  - The name of your ticket panel embed from `embeds/core.json`.
- `channel`
  - The channel where the ticket panel with the button will be posted.
- `category`
  - The category where all new ticket channels will be created.
- `ticket_embed`
  - The name of your welcome message embed from `embeds/messages.json`.

After running the command, you will get a success message that includes a **Ticket ID**. You will need this ID for the next step.

---

### **Step 3: Grant Staff Access**

By default, no one besides the ticket creator can see a new ticket. You need to assign roles (e.g., "Support Staff") that should have access to view and manage tickets.

#### **Command Syntax**
`/ticket setup add_role ticket_id:[ID] role:[role]`
#### **Parameters**
- `ticket_id`
  - The ID provided when you created the ticket setup in Step 2.
    - *Tip: If you lose the ID, you can find it by running `/ticket setup list`.*
- `role`
  - The role you want to grant access to. Simply select it from the list that appears.

You can run this command multiple times to add all necessary staff roles.

---

### **Step 4: Remove Staff Access**

To remove a role from accessing tickets. The below will guide you through this.

#### **Command Syntax**
`/ticket setup remove_role ticket_id:[ID] role:[role]`
#### **Parameters**
- `ticket_id`
  - The ID provided when you created the ticket setup in Step 2.
    - *Tip: If you lose the ID, you can find it by running `/ticket setup list`.*
- `role`
  - The role you want to remove access to. Simply select it from the list that appears.

You can run this command multiple times to remove specific staff roles.

---
### 🔒 Captcha Verification

> [!IMPORTANT]
> You **MUST** configure your `.env` file for this to work.
> 
> `CAPTCHA_SYSTEM=` | True/False <br>
> `CAPTCHA_CHANNEL=` | Where the message will be posted <br>
> `CAPTCHA_ROLE=` | Role ID that will be given to the user

#### **Command Syntax**
`/captcha setup post`

#### **Parameters**
None, these are set in your `.env` file!