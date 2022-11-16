# diclipy - CLI python script for posting/reading/commenting on [Diaspora*](http://diasporafoundation.org) pod written around [Diaspy][diaspy] API

## Dependencies:

* python3
* [diaspy][diaspy]
* [clap][clap]

## Usage:

Run `diclipy -h` for help.

Config folder: ~/.diclipy

Doc.: <http://pythonhosted.org/diclipy>

## Install:

`pip3 install diclipy`

or if you get errors try from git:

### clap:

1. download and unpack [clap][clapmaster] repo
2. `cd` to `clap` folder
3. `pip3 install .`

### diaspy:

1. download and unpack [diaspy][diaspymaster] repo
2. `cd` to `diaspy` folder
3. `pip3 install .`

### diclipy:

1. download and unpack [this][diclipymaster] repo
2. `cd` to folder
3. `pip3 install .`

## Help:

```
SYNTAX:
    diclipy [OPTIONS ...] [COMMAND [COMMAND OPTIONS ...]]

OPTIONS:
    -h, --help                  - Display this help.
    -v, --verbose               - Be verbose.
    -d, --debug                 - Print a lot of debug scrap
                                   (WARNING: password too!).
    -V, --version               - Display version information.
    -C, --component <str>       - Which component's version to display:
                                   ui, backend|diaspy, clap.
    -Q, --quiet                 - Be quiet.

   LOGIN OPTIONS:
    -H, --handle HANDLE         - Diaspora* handle (USER@POD) (overrides config)
                                   (not load saved password).
    -P, --password PASSWORD     - Specify password.
    -p, --proto <str>           - Protocol to use (default: 'https').
    -s, --save-auth             - Store auth data as plain json file
                                   (~/.diclipy/auth.json).
    -S, --set-default           - Set default handle (requires: --handle|-H)
                                   (~/.diclipy/defhandle.json).
    -L, --load-auth             - Load saved password associated with handle
                                   being used (default).
    -D, --use-default           - Use default handle (default)
                                   (if not set you'll be asked for login data).

   EXAMPLES:
     Save auth to file & set default handle:
       diclipy -sS [...]
      or:
       diclipy -sSH USER@POD [...]
      or:
       diclipy -sSH USER@POD -P PASSWORD [...]
      or save only password:
       diclipy -s [...]
      or only set default handle:
       diclipy -S [...]

     Load saved password & use default handle (default):
       diclipy -LD [...]

     Show version:
       diclipy -V -C ui
       diclipy -v -V -C backend
       diclipy -vVC clap

COMMAND:
    post                        - operations with posts.
    notifs                      - operations with notifications.

COMMAND OPTIONS:
   `post` command options:
        -m, --message "MESSAGE" - Send post with given message
                                   (conflicts: --read, --reshare)
                                   if "MESSAGE" = "-" then read data from stdin.
        -A, --aspect ID      - Aspect ID to send post to (default: "public")
                                   ("public", "all", or aspect ID number)
                                   you can find aspect numeric value at your
                                   Diaspora contacts page in aspects links list
                                   e.g.: for 'https://POD/contacts?a_id=1234567'
                                   aspect ID is: '1234567'.
        -i, --image "PATH"      - Attach image to post.
        -r, --read              - Read post of given ID (conflicts: --message).
        -a, --also-comments     - Read also post comments (requires: --read).
        -R, --reshare           - Reshare post of given ID
                                   (conflicts: --message).
        -c, --comment "COMMENT" - Comment the post of given ID
                                   (conflicts: --message)
                                   if "COMMENT" = "-" read from stdin.
        -l, --like              - Like the post of given ID
                                   (conflicts: --message).
        -I, --id ID          - Supplies post ID
                                   (for: --read, --reshare, --comment, --like).
        -s, --stdin             - Read data from --message|--comment arg
                                   and + system standart input
                                   (requires: --message|--comment).

   `notifs` (notifications) command options:
        -l, --last              - Check your unread notifications.
        -U, --unread-only       - Display only unread notifications.
        -r, --read              - Mark listed notifications as read
                                   (by default notifications are not marked).
        -p, --page N            - Print N-th page of notifications.
        -P, --per-page N        - Print N notifications per page.

    EXAMPLES:
      SEND THE POST:
        diclipy post -m "MESSAGE"
        diclipy -H USER@POD -P PASSWORD post -m "MESSAGE"
        diclipy post -A ASPECT_ID -m "MESSAGE"
        diclipy post -m "MESSAGE WITH
         LINE BREAKS,
         PIC & TAGS
         ![](PICTURE.JPG)
         #TAG1 #TAG2 #TAG3"

      SEND THE POST FROM SYSTEM STDIN:
        diclipy post -m -
         ... TYPE MESSAGE (multiline acceptably) & PRESS: Ctrl+d
        diclipy post -sm ''
         ... TYPE MESSAGE & PRESS: Ctrl+d
        echo "It's a post through pipe!" | diclipy post -m -
        diclipy post -m - <<<"It's a stdin post again! Whoo!"
        diclipy post -m - <<EOF
         It's a stdin post
         with line breaks!
         Yay!
         EOF

      READ THE POST OF GIVEN ID:
        diclipy post -rI ID

      READ THE POST OF GIVEN ID + COMMENTS:
        diclipy post -raI ID

      RESHARE THE POST OF GIVEN ID:
        diclipy post -RI ID

      LIKE THE POST OF GIVEN ID:
        diclipy post -lI ID

      COMMENTING POST OF GIVEN ID:
        diclipy post -I ID -c "COMMENT"
        diclipy post -I ID -c "COMMENT WITH
         LINE
         BREAKS"

      COMMENTING POST OF GIVEN ID FROM SYSTEM STDIN:
        diclipy post -I ID -c -
         ... TYPE COMMENT & PRESS: Ctrl+d
        diclipy post -I ID -sc ''
         ... TYPE COMMENT & PRESS: Ctrl+d
        echo "It's a comment through pipe!" | diclipy post -I ID -c -
       BE VERBOSE:
        diclipy -v post -I ID -c - <<<"It's stdin again!"
        diclipy -v post -I ID -c - <<EOF
         It's a
         multiline
         stdin
         comment!
         EOF

      READ YOUR UNREAD NOTIFICATIONS:
       READ LAST:
        diclipy notifs --last
        diclipy notifs -l
       READ LAST 20 PER PAGE:
        diclipy notifs --last --per-page 20
        diclipy notifs --page 2 --per-page 20
        diclipy notifs -p 2 -P 20

--
diacli: Copyright Marek Marecki (c) 2013 https://github.com/marekjm/diacli
 This is free software published under GNU GPL v3 license
 or any later version of this license.

diclipy: Copyleft uzver(at)protonmail.ch (ɔ) 2022
```

[diclipy]: https://notabug.org/uzver/diclipy
[diclipymaster]: https://notabug.org/uzver/diclipy/archive/master.zip
[diaspy]: https://github.com/marekjm/diaspy
[diaspymaster]: https://github.com/marekjm/diaspy/archive/refs/heads/master.zip
[clap]: https://github.com/marekjm/clap
[clapmaster]: https://github.com/marekjm/clap/archive/refs/heads/devel.zip
