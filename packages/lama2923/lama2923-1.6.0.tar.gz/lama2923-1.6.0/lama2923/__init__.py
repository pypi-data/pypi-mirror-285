import os
import time
import socket
from colorama import Fore, Style, init
import requests
import sys
import datetime


if os.name == 'nt':
    import msvcrt
    

init()

def clear_screen():
    if os.name == 'posix':
        os.system('clear')
    elif os.name == 'nt':
        os.system('cls')
    else:
        raise NotImplementedError("Unsupported Operating System!")

def calculate_elapsed_time(start_time, end_time):
    if not (isinstance(start_time, (int, float)) and isinstance(end_time, (int, float))):
        raise TypeError("Only time.time() or get_time() values are accepted!")

    time_difference = end_time - start_time
    seconds = int(time_difference)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(hours, 60)
    days, hours = divmod(hours, 24)
    milliseconds = int((time_difference - int(time_difference)) * 100)
    
    return {
        "Milliseconds": milliseconds,
        "Seconds": seconds if seconds > 0 else None,
        "Minutes": minutes if minutes > 0 else None,
        "Hours": hours if hours > 0 else None,
        "Days": days if days > 0 else None
    }

def get_time():
    return time.time()
    
def rainbow_text(TEXT, LOOP, Speed, section):
    def speed_control():
        if Speed not in ['Slow', 'Fast', None]:
            raise ValueError("Invalid speed value. Choose 'Slow', 'Fast', or None.")

    def section_control():
        if section not in ['Full', 'Half', 'Quarter', None]:
            raise ValueError("Invalid section value. Choose 'Full', 'Half', 'Quarter', or None.")

    speed_control()
    section_control()      
    
    init(autoreset=True)
    if not isinstance(LOOP, int):
        print("LOOP must be an integer!")
        time.sleep(3)
        clear_screen()
        exit(1)

    colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.BLUE, Fore.MAGENTA, Fore.CYAN]

    text_length = len(TEXT)
    
    if section in ['Full', None]:
        section_count1 = 238
        section_count2 = section_count1 - 2
    elif section == 'Half':
        section_count1 = 119
        section_count2 = section_count1 - 2
    elif section == 'Quarter':
        section_count1 = 59
        section_count2 = section_count1 - 2 
               
    while True:
        if LOOP <= 0:
            break
        
        for i in range(1, section_count1 - text_length):
            for color in colors:
                if Speed in ['Slow']:
                    time.sleep(0.001)  
                elif Speed == 'Fast':
                    pass
                elif Speed is None:
                    time.sleep(0.0001)    
                print(" " * i + color + TEXT)

        for i in range(section_count2 - text_length, 0, -1):
            for color in colors:
                if Speed in ['Slow']:
                    time.sleep(0.001)  
                elif Speed == 'Fast':
                    pass
                elif Speed is None:
                    time.sleep(0.0001)   
                print(" " * i + color + TEXT)

def check_port(ip_address, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((ip_address, port))
    sock.close()

    return result == 0

def check_internet():
    try:
        response = requests.get("http://www.google.com", timeout=2.5)
        return True
    except requests.ConnectionError:
        return False

def lprint(*text, end="\n", sep=" ", delay=0.10):
    text = map(str, text)
    combined_word = sep.join(text)
    word_len = len(combined_word)

    for char in combined_word:
        print(char, end="", flush=True)
        time.sleep(delay)

    print(end=end)

def clear_autocorrect():
    if os.name == 'nt':
        while msvcrt.kbhit():
            msvcrt.getch()

def linput(*text, end="", sep=" ", delay=0.10, autocorrect=False):
    lprint(*text, end=end, sep=sep, delay=delay)
    if autocorrect and os.name == 'nt':
        clear_autocorrect()
    return input()

def formatted_number(Numbers=0):
    if not isinstance(Numbers, (int, float, str)):
        raise TypeError("Value must be an integer, float, or a numeric string.")
    
    Numbers = str(float(Numbers)).replace('.', ',')
    integer_part, fractional_part = Numbers.split(',')

    formatted_integer_part = ".".join([
        integer_part[max(i - 3, 0):i]
        for i in range(len(integer_part), 0, -3)
    ][::-1])

    return f"{formatted_integer_part},{fractional_part}"

def reverse_formatted_number(Numbers=0):
    if not isinstance(Numbers, str):
        raise TypeError("Value must be a string.")
    return Numbers.replace(".", "").replace(",", ".")

def clear_autocorrect():
    if os.name == 'nt':
        while msvcrt.kbhit():
            msvcrt.getch()

def llinput(*prompt, sep=" ", end='\n', wend='', max_length=None, min_lenght=None, forceint=False, negativeint=False, forcestr = False, forceinput=False, startswith = ("", False), forcestartswith=[], forceendswith = [], choices = ([], False), blockedchars = r"", availablechars=r"", forceinputlen=0, autocorrect=False, inputcolor=None, promptcolor=None, endcolor=None, wendcolor=None):
    prompt = sep.join(map(str, prompt))
    
    bool_values = [forcestr, forceint, negativeint]
    true_count = bool_values.count(True)

    if true_count > 1:
        raise ValueError("forcestr, forceint, and negativeint cannot be used together.")
    
    
    if os.name == "nt" and autocorrect:
        clear_autocorrect()
    
    
    Choices_VALUE = False
    
    colors = {
        "red": Fore.RED,
        "green": Fore.GREEN,
        "yellow": Fore.YELLOW,
        "blue": Fore.BLUE,
        "magenta": Fore.MAGENTA,
        "cyan": Fore.CYAN,
        "white": Fore.WHITE,
        "black": Fore.BLACK,
    }
    

    
    if os.name != 'nt':
        raise NotImplementedError("This function is only implemented for Windows systems.")
    
    sys.stdout.write(prompt)
    sys.stdout.flush()

    input_str = startswith[0]
    

    if inputcolor is not None:
        inputcolor = colors.get(inputcolor.lower())
        if inputcolor is None:
            inputcolor = ""
    else:
        inputcolor = ""
    if promptcolor is not None:
        promptcolor = colors.get(promptcolor.lower())
        if promptcolor is None:
            promptcolor = ""
    else:
        promptcolor = ""
    if endcolor is not None:
        endcolor = colors.get(endcolor.lower())
        if endcolor is None:
            endcolor = ""
    else:
        endcolor = ""
    if wendcolor is not None:
        wendcolor = colors.get(wendcolor.lower())
        if wendcolor is None:
            wendcolor = ""
    else:
        wendcolor = ""
    
    
    
    def update_display():
        if any([promptcolor, inputcolor, wendcolor, endcolor]):
            sys.stdout.write('\r' + promptcolor + prompt + Fore.RESET + inputcolor + input_str + Fore.RESET + wendcolor + wend + Fore.RESET + ' ' * (len(end) + 1))
            sys.stdout.write('\r' + promptcolor + prompt + Fore.RESET + inputcolor + input_str + Fore.RESET + wendcolor + wend + Fore.RESET )
            sys.stdout.write('\b' * len(wend))
            sys.stdout.flush()
        else:
            sys.stdout.write('\r' + prompt + input_str + wend + ' ' * (len(end) + 1))
            sys.stdout.write('\r' + prompt + input_str + wend)
            sys.stdout.write('\b' * len(wend))
            sys.stdout.flush()

    update_display()  
    if os.name == "nt":
        while True:
            ch = msvcrt.getwch()  
            
            if availablechars:
                if not ch in availablechars and not ch in {'\r', '\n', "\b", "\x7f"}:
                    continue
            
            if ch in blockedchars:
                continue
            
            
            if forcestartswith:
                if ch in {'\r', '\n', "\b", "\x7f"}:
                    pass
                else:
                    match_found = False
                    for fs in forcestartswith:
                        if input_str.startswith(fs) or (len(input_str) < len(fs) and ch == fs[len(input_str)]):
                            match_found = True
                            break
                    if not match_found:
                        continue

            
            if ch in {'\r', '\n'}:  # Enter key
                if choices[0]:
                    if not choices[1]:
                        cvb = False
                        for c in choices[0]:
                            if input_str == c:
                                cvb = True
                                break
                        if not cvb:
                            continue
                    else:
                        cvb = False
                        for c in choices[0]:
                            if input_str.lower() == c.lower():
                                cvb = True
                                Choices_VALUE = c
                                break
                        
                        if not cvb:
                            continue
                
                
                if forceendswith != []:
                    cbv = False
                    for f in forceendswith:
                        if input_str.endswith(f):
                            cbv = True
                            break
                    
                    if not cbv:
                        continue
                
                if forceinput:
                    if input_str == "":
                        continue
                
                
                if forceinputlen > 0:
                    if len(input_str) != forceinputlen:
                        continue
                    
                if min_lenght is not None:
                    if len(input_str) < min_lenght:
                        continue    
                
                break
            elif ch in {'\b', '\x7f'}:  # Backspace key
                
                if len(input_str) > 0:
                    if startswith[1]:
                        if len(input_str) == len(startswith[0]):
                            pass
                        else:
                            input_str = input_str[:-1]

                    else:
                        input_str = input_str[:-1]
            

                    
            else:
                if max_length is None or len(input_str) < max_length:
                    if forceint:
                        if ch.isdigit():
                            input_str += ch
                        else:
                            if negativeint:
                                if ch == "-":
                                    if len(input_str) == 0:
                                        input_str += ch
                    elif negativeint and not forcestr:
                        if ch == "-":
                            if len(input_str) == 0:
                                input_str += ch
                        else:
                            if ch.isdigit() and input_str[0] == "-":
                                input_str += ch
                        
                    else:
                        if forcestr:
                            try:
                                int(ch)
                            except ValueError:
                                input_str += ch
                        else:
                            input_str += ch


            update_display()
        if any([promptcolor, inputcolor, wendcolor, endcolor]):
            sys.stdout.write('\r' + promptcolor + prompt + Fore.RESET + inputcolor + input_str + Fore.RESET + wendcolor + wend + Fore.RESET + endcolor + end + Fore.RESET)
            sys.stdout.flush()
        else:
            sys.stdout.write('\r' + prompt + input_str + wend + end)
            sys.stdout.flush()
            
        if Choices_VALUE:
            return Choices_VALUE
        else:
            return input_str



class _Tools:
    def __init__(self):
        pass
    
    @staticmethod
    def control_file(file_name):
        return os.path.exists(file_name)
        
    @staticmethod
    def format_embed(embed):
        formatted_embed = {}
        all_args3 = {'fields': ['name', 'value', 'inline']}
        all_args2 = {'footer': ['text', 'icon_url'], 'image': ['url'], 'thumbnail': ['url']}
        all_args1 = ['title', 'description', 'color', 'url']

        for arg in all_args1:
            if arg in embed:
                formatted_embed[arg] = embed[arg]

        for arg, keys in all_args2.items():
            if arg in embed:
                formatted_embed[arg] = {key: embed[arg][key] for key in keys if key in embed[arg]}

        if 'fields' in embed:
            formatted_embed['fields'] = [
                {arg: field[arg] for arg in all_args3['fields'] if arg in field}
                for field in embed['fields']
            ]

        return formatted_embed
    
    @staticmethod
    def upload_image(image_path):
        try:
            url = "https://catbox.moe/user/api.php"
            payload = {
                'reqtype': 'fileupload'
            }
            files = {
                'fileToUpload': open(image_path, 'rb')
            }
            response = requests.post(url, data=payload, files=files)

            if response.status_code == 200:
                return response.text.strip()
            else:
                return None
        except:
            return None
        
    
    

    
    @staticmethod
    def url_check(url):
        try:
            response = requests.head(url, allow_redirects=True)
            if response.status_code == 200:
                return True
            else:
                return False
        except requests.exceptions.RequestException as e:
            return False

class TokenIsNotWork(Exception):
    pass

class Discord:
    
    class Embed:
        def __init__(self, title=None, description=None, color=0x3498db):
            self.embed = {
                "title": title,
                "description": description,
                "color": color,
                "fields": [],
                "author": {},
                "footer": {},
                "thumbnail": {},
                "image": {},
                "timestamp": None
            }

        def set_author(self, name, icon_url_or_path=None, url=None):
            icon_url = None
            if icon_url_or_path:
                if icon_url_or_path.startswith("http"):
                    if _Tools.url_check(icon_url_or_path):
                        icon_url = icon_url_or_path
                    else:
                        raise ValueError("URL is not valid.")
                else:
                    if _Tools.control_file(icon_url_or_path):
                        icon_url = _Tools.upload_image(icon_url_or_path)
                        if icon_url is None:
                            raise Exception("Image upload failed", icon_url_or_path)
                    else:
                        raise FileNotFoundError(f"File not found: {icon_url_or_path}")
                    
            self.embed["author"] = {"name": name, "icon_url": icon_url, "url": url}

        def add_field(self, name, value, inline=True):
            self.embed["fields"].append({"name": name, "value": value, "inline": inline})

        def set_footer(self, text, icon_url_or_path=None):
            icon_url = None
            if icon_url_or_path:
                if icon_url_or_path.startswith("http"):
                    if _Tools.url_check(icon_url_or_path):
                        icon_url = icon_url_or_path
                    else:
                        raise ValueError("URL is not valid.")
                else:
                    if _Tools.control_file(icon_url_or_path):
                        icon_url = _Tools.upload_image(icon_url_or_path)
                        if icon_url is None:
                            raise Exception("Image upload failed", icon_url_or_path)
                    else:
                        raise FileNotFoundError(f"File not found: {icon_url_or_path}")
                    
            self.embed["footer"] = {"text": text, "icon_url": icon_url}

        def set_thumbnail(self, url_or_path):
            url = None
            if url_or_path:
                if url_or_path.startswith("http"):
                    if _Tools.url_check(url_or_path):
                        url = url_or_path
                    else:
                        raise ValueError("URL is not valid.")
                else:
                    if _Tools.control_file(url_or_path):
                        url = _Tools.upload_image(url_or_path)
                        if url is None:
                            raise Exception("Image upload failed", url_or_path)
                    else:
                        raise FileNotFoundError(f"File not found: {url_or_path}")
                    
            self.embed["thumbnail"] = {"url": url}

        def set_image(self, url_or_path):
            url = None
            if url_or_path:
                if url_or_path.startswith("http"):
                    if _Tools.url_check(url_or_path):
                        url = url_or_path
                    else:
                        raise ValueError("URL is not valid.")
                else:
                    if _Tools.control_file(url_or_path):
                        url = _Tools.upload_image(url_or_path)
                        if url is None:
                            raise Exception("Image upload failed", url_or_path)
                    
                    else:
                        raise FileNotFoundError(f"File not found: {url_or_path}")
            else:
                raise ValueError("URL or path must be specified.")
            
            self.embed["image"] = {"url": url}

        def set_timestamp(self, timestamp=None):
            self.embed["timestamp"] = timestamp if timestamp else datetime.datetime.utcnow().isoformat()

    
    class Author:
        def __init__(self, token):
            self.token = str(token)
            response = requests.get('https://discord.com/api/v9/users/@me', headers={'Authorization': self.token})
            if response.status_code != 200:
                raise TokenIsNotWork('Token : \'{}\' is not working!'.format(self.token))
            
        def send_message(self, Channel_id, Message, files=None):
            not_files = []
            
            if files:
                for file in files:
                    if not _Tools.control_file(file):
                        not_files.append(file)
                        
            if not_files: 
                raise FileNotFoundError(f"Files not found: {', '.join(not_files)}")
        
            payload = {'content': str(Message)}
            headers = {'Authorization': self.token}


            if files is not None and isinstance(files, list):
                files_data = {}
                for file_name in files:
                    if os.path.exists(file_name) and os.path.getsize(file_name) > 0:
                        with open(file_name, "rb") as file:
                            files_data[os.path.basename(file_name)] = file.read()


                if files_data:
                    response = requests.post(f'https://discord.com/api/v9/channels/{Channel_id}/messages', data=payload, files=files_data, headers=headers)
                else:
                    response = requests.post(f'https://discord.com/api/v9/channels/{Channel_id}/messages', data=payload, headers=headers)
            else:
                response = requests.post(f'https://discord.com/api/v9/channels/{Channel_id}/messages', data=payload, headers=headers)

            return response.status_code

        def send_reply_message(self, Channel_id, Message, ReplyMessage_id, files=None):
            not_files = []
            
            if files:
                for file in files:
                    if not _Tools.control_file(file):
                        not_files.append(file)
                        
            if not_files: 
                raise FileNotFoundError(f"Files not found: {', '.join(not_files)}")
            
            payload = {'content': str(Message), 'message_reference': {'message_id': ReplyMessage_id}}
            headers = {'Authorization': self.token}

    
            if files is not None and isinstance(files, list):
                files_data = {}
                for file_name in files:
                    if os.path.exists(file_name) and os.path.getsize(file_name) > 0:
                        with open(file_name, "rb") as file:
                            files_data[os.path.basename(file_name)] = file.read()
 
    
                if files_data:
                    response = requests.post(f'https://discord.com/api/v9/channels/{Channel_id}/messages', data=payload, files=files_data, headers=headers)
                else:
                    response = requests.post(f'https://discord.com/api/v9/channels/{Channel_id}/messages', data=payload, headers=headers)
            else:
                response = requests.post(f'https://discord.com/api/v9/channels/{Channel_id}/messages', data=payload, headers=headers)
    
            return response.status_code

        def delete_message(self, Channel_id, Message_id):
            headers = {'Authorization': self.token}
            response = requests.delete(f'https://discord.com/api/v9/channels/{Channel_id}/messages/{Message_id}', headers=headers)
            return response.status_code
        
        def edit_message(self, Channel_id, Message_id, Message_Content):
            headers = {'Authorization': self.token}
            payload = {'content': str(Message_Content)}
            response = requests.patch(f'https://discord.com/api/v9/channels/{Channel_id}/messages/{Message_id}', json=payload, headers=headers)
            return response.status_code
        
        def get_channel_messages(self, channel_id, limit=50):
            headers = {'Authorization': self.token}
            all_messages = []
            last_message_id = None
    
            while len(all_messages) < limit:
                params = {'limit': min(50, limit - len(all_messages))}
                if last_message_id:
                    params['before'] = last_message_id
    
                response = requests.get(f'https://discord.com/api/v9/channels/{channel_id}/messages', headers=headers, params=params)
                if response.status_code != 200:
                    return response.status_code, response.json() if response.status_code == 200 else response.status_code
    
                messages = response.json()
                if not messages:
                    break
                
                all_messages.extend(messages)
                last_message_id = messages[-1]['id']
    
                if len(messages) < 50:
                    break
                
            return 200, all_messages
          
    
        def get_channel_message(self, Channel_id, Message_id):
            headers = {'Authorization': self.token}
            response = requests.get(f'https://discord.com/api/v9/channels/{Channel_id}/messages/{Message_id}', headers=headers)
            return response.status_code, response.json() if response.status_code == 200 else response.status_code

        def add_reaction(self, Channel_id, Message_id, emoji):
            headers = {'Authorization': self.token}
            emoji = requests.utils.quote(emoji)
            response = requests.put(f'https://discord.com/api/v9/channels/{Channel_id}/messages/{Message_id}/reactions/{emoji}/@me', headers=headers)
            return response.status_code
        
        def remove_reaction(self, Channel_id, Message_id, emoji):
            headers = {'Authorization': self.token}
            emoji = requests.utils.quote(emoji)
            response = requests.delete(f'https://discord.com/api/v9/channels/{Channel_id}/messages/{Message_id}/reactions/{emoji}/@me', headers=headers)
            return response.status_code

        def get_channel_info(self, Channel_id):
            headers = {'Authorization': self.token}
            response = requests.get(f'https://discord.com/api/v9/channels/{Channel_id}', headers=headers)
            return response.status_code, response.json() if response.status_code == 200 else response.status_code
    
        def get_guild_channels(self, Guild_id):
            headers = {'Authorization': self.token}
            response = requests.get(f'https://discord.com/api/v9/guilds/{Guild_id}/channels', headers=headers)
            return response.status_code, response.json() if response.status_code == 200 else response.status_code   

        
        def change_user_nickname(self, Guild_id, Nickname):
            headers = {'Authorization': self.token}
            payload = {'nick': str(Nickname)}
            response = requests.patch(f'https://discord.com/api/v9/guilds/{Guild_id}/members/@me/nick', json=payload, headers=headers)
            return response.status_code

        def get_author_info(self):
            headers = {'Authorization': self.token}
            response = requests.get('https://discord.com/api/v9/users/@me', headers=headers)
            return response.status_code, response.json() if response.status_code == 200 else response.status_code
        
        def get_author_relationships(self):
            headers = {'Authorization': self.token}
            response = requests.get('https://discord.com/api/v9/users/@me/relationships', headers=headers)
            return response.status_code, response.json() if response.status_code == 200 else response.status_code
        
        def send_friend_request(self, User_id):
            headers = {'Authorization': self.token}
            response = requests.put(f'https://discord.com/api/v9/users/@me/relationships/{User_id}', headers=headers)
            return response.status_code
        
        def remove_friend(self, User_id):
            headers = {'Authorization': self.token}
            response = requests.delete(f'https://discord.com/api/v9/users/@me/relationships/{User_id}', headers=headers)
            return response.status_code
        
        def block_user(self, User_id):
            headers = {'Authorization': self.token}
            response = requests.put(f'https://discord.com/api/v9/users/@me/relationships/{User_id}/block', headers=headers)
            return response.status_code
        
        def unblock_user(self, User_id):
            headers = {'Authorization': self.token}
            response = requests.delete(f'https://discord.com/api/v9/users/@me/relationships/{User_id}/block', headers=headers)
            return response.status_code

        def get_author_channels(self):
            headers = {'Authorization': self.token}
            response = requests.get('https://discord.com/api/v9/users/@me/channels', headers=headers)
            return response.status_code, response.json() if response.status_code == 200 else response.status_code
        
        def get_author_guilds(self):
            headers = {'Authorization': self.token}
            response = requests.get('https://discord.com/api/v9/users/@me/guilds', headers=headers)
            return response.status_code, response.json() if response.status_code == 200 else response.status_code
        
        def get_author_settings(self):
            headers = {'Authorization': self.token}
            response = requests.get('https://discord.com/api/v9/users/@me/settings', headers=headers)
            return response.status_code, response.json() if response.status_code == 200 else response.status_code
            
        def get_author_connections(self):
            headers = {'Authorization': self.token}
            response = requests.get('https://discord.com/api/v9/users/@me/connections', headers=headers)
            return response.status_code, response.json() if response.status_code == 200 else response.status_code
        
        def get_user_info(self, User_id):
            headers = {'Authorization': self.token}
            response = requests.get(f'https://discord.com/api/v9/users/{User_id}', headers=headers)
            return response.status_code, response.json() if response.status_code == 200 else response.status_code

        def get_all_guilds(self):
            headers = {'Authorization': self.token}
            response = requests.get('https://discord.com/api/v9/users/@me/guilds', headers=headers)
            return response.status_code, response.json() if response.status_code == 200 else response.status_code
        
        def get_guild(self, Guild_id):
            headers = {'Authorization': self.token}
            response = requests.get(f'https://discord.com/api/v9/guilds/{Guild_id}', headers=headers)
            return response.status_code, response.json() if response.status_code == 200 else response.status_code
            
        def kick_member(self, Guild_id, Member_id):
            headers = {'Authorization': self.token}
            response = requests.delete(f'https://discord.com/api/v9/guilds/{Guild_id}/members/{Member_id}', headers=headers)
            return response.status_code
        
        def ban_member(self, Guild_id, Member_id, delete_message_days=0):
            headers = {'Authorization': self.token}
            data = {'delete_message_days': delete_message_days}
            response = requests.put(f'https://discord.com/api/v9/guilds/{Guild_id}/bans/{Member_id}', headers=headers, json=data)
            return response.status_code
        
        def unban_member(self, Guild_id, Member_id):
            headers = {'Authorization': self.token}
            response = requests.delete(f'https://discord.com/api/v9/guilds/{Guild_id}/bans/{Member_id}', headers=headers)
            return response.status_code
        
        def get_guild_bans(self, Guild_id):
            headers = {'Authorization': self.token}
            response = requests.get(f'https://discord.com/api/v9/guilds/{Guild_id}/bans', headers=headers)
            return response.status_code, response.json() if response.status_code == 200 else response.status_code
            
        def get_guild_channels(self, Guild_id):
            headers = {'Authorization': self.token}
            response = requests.get(f'https://discord.com/api/v9/guilds/{Guild_id}/channels', headers=headers)
            return response.status_code, response.json() if response.status_code == 200 else response.status_code
        
        def get_guild_members(self, Guild_id):
            headers = {'Authorization': self.token}
            response = requests.get(f'https://discord.com/api/v9/guilds/{Guild_id}/members', headers=headers)
            return response.status_code, response.json() if response.status_code == 200 else response.status_code
            
        def get_guild_roles(self, Guild_id):
            headers = {'Authorization': self.token}
            response = requests.get(f'https://discord.com/api/v9/guilds/{Guild_id}/roles', headers=headers)
            return response.status_code, response.json() if response.status_code == 200 else response.status_code
            
        def get_user_connections(self, id):
            headers = {'Authorization': self.token}
            response = requests.get(f'https://discord.com/api/v9/users/{id}/connections', headers=headers)
            return response.status_code, response.json() if response.status_code == 200 else response.status_code
        
        def join_channel(self, Channel_id):
            headers = {'Authorization': self.token}
            response = requests.put(f'https://discord.com/api/v9/channels/{Channel_id}/call/join', headers=headers)
            return response.status_code

        def leave_channel(self, Channel_id):
            headers = {'Authorization': self.token}
            response = requests.delete(f'https://discord.com/api/v9/channels/{Channel_id}/call', headers=headers)
            return response.status_code

        
        
        def get_channel_call(self, Channel_id):
            headers = {'Authorization': self.token}
            response = requests.get(f'https://discord.com/api/v9/channels/{Channel_id}/call', headers=headers)
            return response.status_code, response.json() if response.status_code == 200 else response.status_code
        
        def play_sound(self, Channel_id, Sound):
            headers = {'Authorization': self.token}
            payload = {'audio': str(Sound)}
            response = requests.post(f'https://discord.com/api/v9/channels/{Channel_id}/call/ring', json=payload, headers=headers)
            return response.status_code

        def create_guild(self, Guild_name, Region='europe', Verification_level=0, Default_message_notifications=0, Explicit_content_filter=0, Roles=None, Channels=None):
            headers = {'Authorization': self.token}
            payload = {
                'name': str(Guild_name),
                'region': str(Region),
                'verification_level': int(Verification_level),
                'default_message_notifications': int(Default_message_notifications),
                'explicit_content_filter': int(Explicit_content_filter)
            }
            if Roles is not None and isinstance(Roles, list):
                payload['roles'] = Roles
            if Channels is not None and isinstance(Channels, list):
                payload['channels'] = Channels
            response = requests.post('https://discord.com/api/v9/guilds', json=payload, headers=headers)
            return response.status_code
    
        def delete_guild(self, Guild_id):
            headers = {'Authorization': self.token}
            response = requests.delete(f'https://discord.com/api/v9/guilds/{Guild_id}', headers=headers)
            return response.status_code

       

        def edit_guild(self, Guild_id, Guild_name, Region='europe', Verification_level=0, Default_message_notifications=0, Explicit_content_filter=0, Roles=None, Channels=None):
            headers = {'Authorization': self.token}
            payload = {
                'name': str(Guild_name),
                'region': str(Region),
                'verification_level': int(Verification_level),
                'default_message_notifications': int(Default_message_notifications),
                'explicit_content_filter': int(Explicit_content_filter)
            }
            if Roles is not None and isinstance(Roles, list):
                payload['roles'] = Roles
            if Channels is not None and isinstance(Channels, list):
                payload['channels'] = Channels
            response = requests.patch(f'https://discord.com/api/v9/guilds/{Guild_id}', json=payload, headers=headers)
            return response.status_code
        
        def create_guild_role(self, Guild_id, Role_name):
            headers = {'Authorization': self.token}
            payload = {'name': str(Role_name)}
            response = requests.post(f'https://discord.com/api/v9/guilds/{Guild_id}/roles', json=payload, headers=headers)
            return response.status_code
        
        def delete_guild_role(self, Guild_id, Role_id):
            headers = {'Authorization': self.token}
            response = requests.delete(f'https://discord.com/api/v9/guilds/{Guild_id}/roles/{Role_id}', headers=headers)
            return response.status_code

    class Webhook:
        def __init__(self, webhook_url):
            self.WebhookUrl = str(webhook_url)
            
        def send_webhook(self, Content='', embeds=[], files=None):
            not_files = []
            
            if files:
                for file in files:
                    if not _Tools.control_file(file):
                        not_files.append(file)
                        
            if not_files: 
                raise FileNotFoundError(f"Files not found: {', '.join(not_files)}")
            
    
            data = {'content': Content}
            data['embeds'] = []
            if isinstance(embeds, list) or isinstance(embeds, tuple):
                for embed in embeds:
                    if embed:
                        if hasattr(embed, 'embed'):
                            data['embeds'].append(_Tools.format_embed(embed.embed))
                        else:
                            data['embeds'].append(_Tools.format_embed(embed))
            else:
                if embeds:
                    if hasattr(embeds, 'embed'):
                        data['embeds'].append(_Tools.format_embed(embeds.embed))
                    else:
                        data['embeds'].append(_Tools.format_embed(embeds))
            
            if files and isinstance(files, list):
                files_data = {os.path.basename(file_name): open(file_name, "rb").read() for file_name in files if os.path.getsize(file_name) > 0}
                response = requests.post(self.WebhookUrl, data=data, files=files_data)
            else:
                response = requests.post(self.WebhookUrl, json=data)
                
            return response.status_code
        
        
        def delete_message(self, Message_id):
            response = requests.delete(f'{self.WebhookUrl}/messages/{Message_id}')
            return response.status_code
        
        def get_message(self, Message_id):
            response = requests.get(f'{self.WebhookUrl}/messages/{Message_id}')
            return response.status_code, response.json() if response.status_code == 200 else response.status_code
            
        def get_webhook_info(self):
            response = requests.get(self.WebhookUrl)
            return response.status_code, response.json() if response.status_code == 200 else response.status_code
                
        def get_messages(self):
            response = requests.get(f'{self.WebhookUrl}/messages')
            return response.status_code, response.json() if response.status_code == 200 else response.status_code
        
        def edit_message(self, Message_id, Content='', embeds=[]):
            data = {'content': Content}
            data['embeds'] = []
            
            if isinstance(embeds, list) or isinstance(embeds, tuple):
                for embed in embeds:
                    if embed:
                        if hasattr(embed, 'embed'):
                            data['embeds'].append(_Tools.format_embed(embed.embed))
                        else:
                            data['embeds'].append(_Tools.format_embed(embed))
            else:
                if embeds:
                    if hasattr(embeds, 'embed'):
                        data['embeds'].append(_Tools.format_embed(embeds.embed))
                    else:
                        data['embeds'].append(_Tools.format_embed(embeds))
            
            response = requests.patch(f'{self.WebhookUrl}/messages/{Message_id}', json=data)
            return response.status_code



