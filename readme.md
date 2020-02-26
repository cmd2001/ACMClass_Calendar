Feature:

A simple calendar with event tags.

Developed with flask framework.

Usage:

First, initialize the database by initdb.py.

If you want to add a event, just execute `addTask.py` and enter event data.

Use `removeTask.py` to remove a task.

Visit `/month/$Year/$month` to get overviews of events in that month.

You can click on the link of an event to get more information about it.

Edit `config.py` to modify administrator password and login status duration.

Added iCal support, you can subscribe calendar events at `https://hostname/calendar.ics`.

GUI administration system is available now, default password is `admin`.

Known Bugs:

None

Todo:

User management

Markdown editor

Contributors:

[Amagi_Yukisaki](https://gitee.com/Amagi_Yukisaki)

[cong258258](https://gitee.com/cong258258)