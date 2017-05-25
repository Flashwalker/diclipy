#!/usr/bin/env python3

"""### D* is for Diaspora* ###
This is a Diaspora* CLIent written using `diaspy` API.
Why? Cause — CLI rocks! \o

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
    post                        - posts operations.
    notifs                      - notifications operations.

COMMAND OPTIONS:
   `post` command options:
        -m, --message "MESSAGE" - Send post with given message
                                   (conflicts: --read, --reshare)
                                   if "MESSAGE" = "-" then read data from stdin.
        -A, --aspect <str>      - Aspect id to send post to (default: "public")
                                   ("public", "all", or aspect id number)
                                   you can find aspect numeric value at your
                                   Diaspora contacts page in aspects links list
                                   e.g.: for 'https://POD/contacts?a_id=1234567'
                                   aspect id is: '1234567'.
        -i, --image "PATH"      - Attach image to post.
        -r, --read              - Read post of given id (conflicts: --message).
        -a, --also-comments     - Read also post comments (requires: --read).
        -R, --reshare           - Reshare post of given id
                                   (conflicts: --message).
        -c, --comment "COMMENT" - Comment the post of given id
                                   (conflicts: --message)
                                   if "COMMENT" = "-" read from stdin.
        -l, --like              - Like the post of given id
                                   (conflicts: --message).
        -I, --id <str>          - Supplies post id
                                   (for: --read, --reshare, --comment, --like).
        -s, --stdin             - Read data from --message|--comment arg
                                   and + system standart input
                                   (requires: --message|--comment).

   `notifs` (short for 'notifications') command options:
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
      READ LAST 10 PER PAGE:
        diclipy notifs --page 1 --per-page 10
        diclipy notifs -p 1 -P 10

--
diacli: Copyright Marek Marecki (c) 2013 https://github.com/marekjm/diacli This is free software published under GNU GPL v3 license or any later version of this license.

diclipy: Copyleft uzver(at)protonmail.ch (ɔ) 2017
"""


import json
import getpass
import os
import re
import sys
import pickle

import diaspy
import clap

__version__ = '0.1.2'

##   Debug for clap
DEBUG = False

if DEBUG:
    import errno
    from pprint import pprint

##   Variables
verbose = False
debug = False
username, pod = '', ''
password = ''
savedconn = {}
proto = 'https'
schemed = ''

def sure_path_exists(path, mode):
    #########
    # try:
    #     os.makedirs(path)
    # except OSError as exception:
    #     if exception.errno != errno.EEXIST:
    #         raise
    #########
    # try: 
    #     os.makedirs(path, mode)
    # except OSError:
    #     if not os.path.isdir(path):
    #         raise
    #########
    os.makedirs(path, mode, exist_ok=True)

def get_authdb():
    ##   Returns dict of stored auth data database.
    if os.path.isfile(os.path.expanduser('~/.diclipy/auth.json')):
        ifstream = open(os.path.expanduser('~/.diclipy/auth.json'))
        try:
            authdb = json.loads(ifstream.read())
        except ValueError:
            authdb = {}
        except (Exception) as e:
            print('\ndiclipy: auth loading: error encountered: {0}'.format(e))
        finally:
            ifstream.close()
    else:
        authdb = {}
    return authdb


def set_default_handle(username, pod):
    ##   Sets default handle.
    sure_path_exists(os.path.expanduser('~/.diclipy'), mode=0o700)
    defhandlepath = os.path.expanduser('~/.diclipy/defhandle.json')
    ofstream = open(defhandlepath, 'w')
    ofstream.write(json.dumps({'username': username, 'pod': pod}))
    ofstream.close()
    os.chmod(defhandlepath, 0o600)

def get_default_handle():
    ##   Returns default handle.
    if os.path.isfile(os.path.expanduser('~/.diclipy/defhandle.json')):
        defhandlepath = os.path.expanduser('~/.diclipy/defhandle.json')
        ifstream = open(defhandlepath)
        try:
            handle = json.loads(ifstream.read())
        except ValueError:
            handle = {'pod': '', 'username': ''}
        except (Exception) as e:
            print('\ndiclipy: handle extraction: error encountered: {0}'.format(e))
        finally:
            ifstream.close()
    else:
        handle = {'pod': '', 'username': ''}
    if debug: print('debug: Found default handle: {0}@{1}'.format(handle['username'], handle['pod']))
    return (handle['username'], handle['pod'])

def get_password():
    global username, pod
    passwd = getpass.getpass('Password for {0}@{1}: '.format(username, pod))
    return passwd

def get_user_input():
    txt = ''
    txtarr = sys.stdin.readlines()
    ##   Drop tailing \n
    txtarr[-1] = txtarr[-1][:-1]
    for line in txtarr:
        txt += line
    return txt

def load_auth():
    global username, pod, password, savedconn, passkey, verbose, debug
    if verbose: print('Loading auth...')
    if not password:
        # password = ''
        authdb = get_authdb()
        passkey = '{0}@{1}'.format(username, pod)
        ##   If key in authdb: password = authdb[key]
        if passkey in authdb:
            try:
                password = authdb[passkey]
            except ValueError:
                password = ''
                print('\ndiclipy: password extraction: ValueError: {0}'.format(e))
            except (Exception) as e:
                print('\ndiclipy: password extraction: error encountered: {0}'.format(e))
            finally:
                if not password:
                    print('Can\'t find password. Is it empty?')
        else:
            print('Can\'t load password. Was it saved?')
    ##   Pickle:
    ##   Load saved connection object:
    ##    we load saved connection data which will be used later...
    connpath = os.path.expanduser('~/.diclipy/{}.connection'.format(passkey))
    if os.path.isfile(connpath):
        f = open(connpath, 'rb')
        try:
            success = False
            savedconn = pickle.load(f)
            if debug: print('debug: savedconn._login_data[\'user[username]\'] = username:')
            savedconn._login_data['user[username]'] = username
            if debug: print('debug: savedconn._login_data[\'user[password]\'] = password:')
            savedconn._login_data['user[password]'] = password
            if debug: print('debug: savedconn._login_data[\'authenticity_token\'] = savedconn._token:')
            savedconn._login_data['authenticity_token'] = savedconn._token
            success = True
        except pickle.UnpicklingError as e:
            print('\ndiclipy: pickle load: problems with the deserialization of the object was hapened: {}'.format(e))
            success = False
        except (Exception) as e:
            print('\ndiclipy: pickle load: error encountered: {0}'.format(e))
            success = False
        except ValueError:
            success = False
        finally:
            f.close()
            if verbose: 
                if success:
                    print('Connection loaded.')
                else:
                    print('Can\'t find saved connection. Will try to get new.')
                    if debug: print('debug: diclipy: load savedconn not success.\n')
            if debug:
                print('debug: type of "savedconn" =', type(savedconn))
                print('debug: savedconn._login_data =', savedconn._login_data)
                print('\ndebug: dir(savedconn):')
                print(dir(savedconn))
                print('\ndebug: savedconn.__dict__:')
                pprint(savedconn.__dict__, indent=2)
                print('')
    else:
        if verbose: print('No saved connection. Will try to get new.')
    return (password, savedconn)

def main():
    global username, pod, password, savedconn, passkey, proto, schemed, verbose, debug
    model = {}
    ##   Creating input list (formating sys agrv)
    ##   Remember to remove the program name from formatter input!
    args = list(clap.formatter.Formatter(sys.argv[1:]).format())
    ##   Detecting location of ui.json file
    uilocation = ''
    ##   cwd ('.') is first to make testing easier
    for path in [('.'), ('', os.getcwd()), ('', os.path.dirname(__file__)), (os.path.expanduser('~'), '.diclipy'), ('', '/usr', 'share', 'diclipy')]:
        path = os.path.join(*path)
        path = os.path.abspath(os.path.join(path, 'ui.json'))
        if DEBUG: print('debug: ui.json path =', path)
        if os.path.isfile(path):
            uilocation = path
            break
    if uilocation:    # if UI file was found - create builder
        with open(uilocation, 'r') as ifstream: model = json.loads(ifstream.read())
    else:           # if it was not - exit with appropriate message
        print('diclipy: fatal: cannot find ui.json file')
        exit(1)
    ###  TODO:
    ##   Add type handlers for the interface
    ##   builder.addTypeHandler('handle', diaspy.people.sephandle)
    ###
    ##   Build the interface
    ##   And get() it
    options = clap.builder.Builder(model).build().get()

    ##   Parse options of ui.json
    parser = clap.parser.Parser(options).feed(args)
    ##   Make an options checker/validator
    checker = clap.checker.RedChecker(parser)
    try:
        success = False
        ##   Check and parse options
        checker.check()
        success = True
        if DEBUG: print('debug: options check success =', str(success))
        if DEBUG: print('debug: options parser =', str(parser))
        if DEBUG: print('debug: options checker =', str(checker))
        if DEBUG: print('debug: options model =', str(model))
    except clap.errors.UnrecognizedModeError as e:
        print('diclipy: fatal: unrecognized mode: {0}'.format(e))
        
    except clap.errors.UnrecognizedOptionError as e:
        print('diclipy: fatal: unrecognized option found: {0}'.format(e))
    except clap.errors.UIDesignError as e:
        print('diclipy: fatal: misdesigned interface: {0}'.format(e))
        
    except clap.errors.RequiredOptionNotFoundError as e:
        print('diclipy: fatal: required option was not found: {0}'.format(e))
    except clap.errors.NeededOptionNotFoundError as e:
        print('diclipy: fatal: at least one of needed options must be passed: {0}'.format(e))
    except clap.errors.MissingArgumentError as e:
        print('diclipy: fatal: missing argument for option: {0}'.format(e))
    except (clap.errors.InvalidArgumentTypeError, diaspy.errors.UserError) as e:
        print('diclipy: fatal: invalid argument for option: {0}'.format(e))
    except clap.errors.ConflictingOptionsError as e:
        print('diclipy: fatal: conflicting options: {0}'.format(e))
    finally:
        if not success:
            print('Wrong options or arguments. Run with \'-h\' for help. Exit.')
            if DEBUG: print('debug: options check success =', success)
            optsui = parser.parse().ui().finalise()
            if DEBUG: print('debug: options parser =', str(parser))
            if DEBUG: print('debug: options checker =', str(checker))
            if DEBUG: print('debug: options model =', str(model))
            if DEBUG: print('debug: options =', str(options))
            if DEBUG: print('debug: passed args =', sys.argv[1:])
            if DEBUG: print('debug: formatted args =', args)
            exit(1)
        optsui = parser.parse().ui().finalise()
    if '--verbose' in optsui:
           verbose = True
    if '--debug' in optsui:
        ##   Print debug scrap
        verbose = True
        debug = True
        import errno
        from pprint import pprint
    if '--version' in optsui:
        """   Print version information.
        By default it is version of the interface (if --verbose then backend
        version is added).

        It is possible to specify component which you version you wnat to get.
        Currently, available components are:
        *   ui:             versionof this interface,
        *   backend/diaspy: version of diaspy backend used,
        *   clap:           version of library used to create user interface,
        """
        if verbose: V = 'diclipy version: {0} (diaspy backend: {1})'.format(__version__, diaspy.__version__)
        else: V = __version__
        if '--component' in optsui:
            component = optsui.get('--component')
            if component == 'ui':
                V = __version__
            elif component in ['diaspy', 'backend']:
                component = 'diaspy'
                V = diaspy.__version__
            elif component == 'clap':
                V = clap.__version__
            else: V = 'diclipy: fatal: there is no \'{0}\' component'.format(component)
            if '--verbose' in optsui and 'fatal:' not in V:
                V = '{0} version: {1}'.format(component, V)
        print(V)
        exit(0)
    if '--help' in optsui:
        ##   Prints help and exits.
        print(__doc__)
        exit(0)
    if '--handle' in optsui:
        username, pod = optsui.get('--handle').split('@', 2)
        if debug: print('debug: handle =', optsui.get('--handle'))
        if debug: print('debug: username =', username)
        if debug: print('debug: pod =', pod)
    elif '--use-default' in optsui: username, pod = get_default_handle()
    else: username, pod = get_default_handle()
    try:
        KeyInrt = False
        fail = True
        if not username: username = input('D* username: ')
        if not pod: pod = input('D* pod: ')
        if '--password' in optsui: password = optsui.get('--password')
        # if ('--load-auth' in optsui or not('--password' in optsui)) and not('--save-auth' in optsui or '--handle' in optsui): password, savedconn = load_auth()
        if '--save-auth' in optsui or '--handle' in optsui: pass
        elif '--load-auth' in optsui: password, savedconn = load_auth()
        else: password, savedconn = load_auth()
        if not password: password = get_password()
        """   If proto is passed on the command line
              the default value will be overwritten by it
        """
        if '--proto' in optsui: proto = optsui.get('--proto')
        ##   Create pod URL from given proto and pod
        if not re.compile('^[a-z]://.*').match(pod): schemed = '{0}://{1}'.format(proto, pod)
        else: schemed = pod
        if debug: print('debug: pod url =', schemed)
        ##   We create connection which will be used later...
        if not savedconn:
            if verbose: print('Trying to get new connection...')
            connection = diaspy.connection.Connection(pod=schemed, username=username, password=password)
        else:
            connection = savedconn
            if verbose: print('Reusing saved connection.')
        if debug:
            print('debug: type of "connection" =', type(connection))
            print('debug: connection._login_data =', connection._login_data)
            print('\ndebug: dir(connection):')
            print(dir(connection))
            print('\ndebug: connection.__dict__:')
            pprint(connection.__dict__, indent=2)
            print('')
        ##   ...and login into a pod
        login = connection.login()
        ###  TODO:
        ##   Handle login error (if connection expired) & get new connection.
        ###
        if debug:
            print('debug: type of "login" =', type(login))
            print('\ndebug: dir(login):')
            print(dir(login))
            print('\ndebug: login.__dict__:')
            pprint(login.__dict__, indent=2)
            print('')
        fail = False
    except (KeyboardInterrupt, EOFError):
        ##   If user cancels the login
        KeyInrt = True
        print()
        print('Keyboard Interrupt. Exit.')
    except (Exception) as e:
        fail = True
        print('diclipy: connection: error encountered: {0}'.format(e))
    finally:
        if KeyInrt:
            ##   User cancelled the operation, exit cleanly
            exit(0)
        if fail:
            ##   Retry to get connection
            try:
                print('Retrying to get connection...')
                connection = diaspy.connection.Connection(pod=schemed, username=username, password=password)
                fail = False
            except (Exception) as e:
                fail = True
                print('diclipy: connection: error encountered: {0}'.format(e))
            finally:
                if fail:
                    exit(1)
                ##   ...and login into a pod
                login = connection.login()
        if '--set-default' in optsui:
            set_default_handle(username, pod)
            if verbose:
                defhandlepath = os.path.expanduser('~/.diclipy/defhandle.json')
                if os.path.isfile(defhandlepath):
                    print('Default handle setted to: {0}@{1}'.format(username, pod))
        if '--save-auth' in optsui:
            ##   Save authorization data for later use
            authdb = get_authdb()
            passkey = '{0}@{1}'.format(username, pod)
            authdb[passkey] = password
            sure_path_exists(os.path.expanduser('~/.diclipy'), mode=0o700)
            ##   Pickle
            ##   Dump obj:
            connpath = os.path.expanduser('~/.diclipy/{}.connection'.format(passkey))
            f = open(connpath, 'wb')
            try:
                success = False
                pickle.dump(connection, f, 3)
                success = True
            except pickle.PicklingError as e:
                print('\ndiclipy: pickle dump: problems with the serialization of the object was hapened: {}'.format(e))
                success = False
            except (Exception) as e:
                print('\ndiclipy: pickle dump: error encountered: {0}'.format(e))
                success = False
            finally:
                f.close()
                if success:
                    os.chmod(connpath, 0o600)
                    if verbose:
                        if os.path.isfile(connpath): print('Connection saved.')
            authdbpath = os.path.expanduser('~/.diclipy/auth.json')
            ofstream = open(authdbpath, 'w')
            authdb = ofstream.write(json.dumps(authdb))
            ofstream.close()
            os.chmod(authdbpath, 0o600)
            if verbose:
                if os.path.isfile(authdbpath): print('Auth saved.')
    """   The `.down()` descends one subcommand down the chain.
          So, in here it will return the main command if no subcommand was passed.
    """
    optsui = optsui.down()
    # if not str(optsui):
    if str(optsui) == '':
        if verbose: print('No command was given. Exit.')
        if debug: print('debug: options =', str(options))
        if debug: print('debug: optsui =', str(optsui))
        ##   If no command was given exit cleanly
        exit(0)
    message = ''
    if str(optsui) == 'post':
        ##   Descend here, since yet another subcommand may have been passed.
        # optsui = optsui.down()
        ##   Post has a sub-modes, each of which is enabled by one of local options.
        if '--message' in optsui:
            ##   Send post to a pod
            if '--image' in optsui:
                ##   If --image is given the photo from the path will be posted
                photo = optsui.get('--image')
            else: photo = ''
            """   User can enter text as a single string encapsulated in ''
                  but to prevent mistakes diclipy
                  will join every string passed as an argument and post it all
            """
            text = """{}""".format(optsui.get('--message')).replace('\\n', '\n')
            # text = """{}""".format([line for line in optsui.get('--message')])
            if ('--stdin') in optsui:
                text += """{}""".format(get_user_input())
            elif optsui.get('--message') == '-':
                # text = """{}""".format(input(prompt)) ##   array with last trailing \n
                # text = """{}""".format(sys.stdin.readlines()) ##   array with last trailing \n
                # text = """{}""".format([line for line in sys.stdin]) ##   array with last trailing \n
                # text = """{}""".format([line.splitlines() for line in sys.stdin]) ##   array with no \n at all
                text = """{}""".format(get_user_input())
                if '--stdin' in optsui:
                    text += """{}""".format(get_user_input())
            aspect_ids = optsui.get('--aspect')
            if aspect_ids:
                aspect = aspect_ids
            else:
                # aspect = ['pubic']
                aspect = 'pubic'
            if debug: print('aspect =', aspect)

            if text or photo:
                ##   If text or photo is given it will be posted
                if verbose: print('Posting ...')
                post = diaspy.streams.Activity(connection).post(text=text, aspect_ids=aspect, photo=photo)
                if debug:
                    print('debug: post:')
                    pprint(post.__dict__(), indent=2)
                    print('\ndebug: post.id:', post['id'])
                    print('debug: post.guid:', post['guid'].replace('\'', ''))
                if len(post['guid'].replace('\'', '')) > 2:
                    pid = post['guid'].replace('\'', '')
                else: pid = repr(post.id)
                message = '** post url: {0}/posts/{1}'.format(schemed, pid)
            else: message = 'diclipy: fatal: nothing to post'
        if '--read' in optsui:
            ##   We need to get id of post which user wants to read
            if '--id' in optsui: pid = optsui.get('--id')
            ##   ...and create an object representing this post
            if verbose:
                print('Loading {} ...'.format(pid))
                post = diaspy.models.Post(connection, pid)
                # output = '{0} ({1}) ({2}):\n{3}\n{4}/posts/{5}\n{6}/posts/{7}'.format(post.author('diaspora_id'), post.author('guid'), post.created_at, post, schemed, post.id, schemed, post['guid'].replace('\'', ''))
                if len(post['guid'].replace('\'', '')) > 2:
                    pid = post['guid'].replace('\'', '')
                else: pid = post['id']
                output = '** {0} ({1}):\n\n{2}\n\n** post url: {3}/posts/{4}'.format(post.author('diaspora_id'), post.author('guid'), post, schemed, pid)
            else:
                post = diaspy.models.Post(connection, pid)
                # output = '{0} ({1}):\n{2}'.format(post.author('name'), post.created_at, post)
                output = '** {0}:\n\n{1}'.format(post.author('name'), post)
            print(output)
            if '--also-comments' in optsui and len(post.comments):
                """   Print comments if --also-comments was passed and there is
                      at least one comment to print
                """
                print('\n** Comments for this post:\n')
                for c in post.comments: print('** {0}\n'.format(repr(c)))
        if '--reshare' in optsui:
            ##   Reshare post of given id
            if '--id' in optsui: pid = optsui.get('--id')
            post = diaspy.models.Post(connection, pid)
            post.reshare()
            if verbose: message = 'diclipy: You reshared {0}\'s post!'.format(post.author('name'))
        if '--comment' in optsui:
            if '--image' in optsui:
                photo = optsui.get('--image')
            else: photo = ''
            text = """{}""".format(optsui.get('--comment')).replace('\\n', '\n')
            if ('--stdin') in optsui:
                text += """{}""".format(get_user_input())
            elif optsui.get('--comment') == '-':
                text = """{}""".format(get_user_input())
                if '--stdin' in optsui:
                    text += """{}""".format(get_user_input())
            ##   Comment on post with given id
            if text or photo:
                if '--id' in optsui: pid = optsui.get('--id')
                post = diaspy.models.Post(connection, pid)
                if verbose: print('Commenting ...')
                comment = post.comment(text)
                if verbose:
                    message = 'diclipy: You commented on {0}\'s post!\n'.format(post.author('name')) 
                    message += '** {0} ({1})\n'.format(post.author('diaspora_id'), post.author('guid'), post, schemed, pid)
                message += '** post url: {0}/posts/{1}'.format(schemed, pid)
            else: message = 'diclipy: fatal: Nothing to send'
        if '--like' in optsui:
            ##   like post with given id
            if '--id' in optsui: pid = optsui.get('--id')
            post = diaspy.models.Post(connection, pid)
            post.like()
            if verbose: message = 'diclipy: You liked {0}\'s post!'.format(post.author('name'))
    elif str(optsui) == 'notifs':
        ##   Descend here, since yet another subcommand may have been passed.
        # ui = optsui.down()
        ##   This command allows user to check his notifications.
        ##   First, we create object representing user's notifications
        if str(optsui) == 'notifs':
            notifications = {}
            try:
                notifications = diaspy.notifications.Notifications(connection)
            except (Exception) as e:
                print('\ndiclipy: notifications: error encountered: {0}'.format(e))
                raise e
            finally:
                # pass
                if debug:
                    print('debug: notifications:')
                    for i in notifications:
                        pprint(str(i), indent=2)
            if '--page' in optsui:
                ##   If user wants to read specific page of notifications
                ##   get the page number
                page = optsui.get('--page')
                if '--per-page' in optsui:
                    ##   Set number of notifications per page according to the value
                    ##   specified on the command line...
                    per_page = optsui.get('--per-page')
                else:
                    ##   ...or set the default value
                    per_page = 5
                ##   Get notifications which match given criteria
                notifs = notifications.get(per_page=per_page, page=page)
            elif '--last' in optsui:
                ##   If user wants to just view his/hers --last notifications
                if '--per-page' in optsui:
                    notifs = notifications.get(per_page=optsui.get('--per-page'), page=1)
                    if debug:
                        for i in notifs:
                            print('debug: --last --per-page notifs =', str(i))
                else:
                    notifs = notifications.last()
                    if debug:
                        for i in notifs:
                            print('debug: --last notifs =', str(i))
            else:
                ##   If none of the above is True no notifications will be printed
                notifs = []
            for n in notifs:
                if not n.unread and '--unread-only' in optsui: continue
                ##   Print every notification found
                # text = repr(n)
                text = str(n)
                about = n.about()
                ##   If the notification is about some post add information about id
                ##   of the post being mentioned
                if type(about) == int: about = '{0}/posts/{1}'.format(schemed, about)
                else: about = ''
                print('** {0} {1}\n'.format(text, about))
                if '--read' in optsui:
                    ##   If --read switch is present notifications will be marked as read
                    n.mark(read=True)
    else:
    ##   Default message for not implememted commands
        message = 'diclipy: fatal: \'{0}\' command not implemented'.format(str(optsui))
    if message: 
        print(message)
        if debug: print('debug: options =', str(options))
        if debug: print('debug: optsui =', str(optsui))

if __name__ == "__main__":
    main()


###  TODO:
##   print commenter guid only if verbose
##   use #EDITOR
##   check photo, reshare, like
##   'delete',
##   'delete_comment',
##   'like',
##   'delete_like',
##   'reshare',
##   'update'
##   cut of plural \n at the end of post/comment
##   -Q, --quiet                 - be quiet.
##   debug
##   >&2
###
