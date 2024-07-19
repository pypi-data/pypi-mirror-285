import os as _os
from simpleworkspace.utility import strings as _strings

def LevelPrint(level:int, msg="", flush=False, end='\n'):
    print(_strings.IndentText(msg, level, indentStyle='    '), flush=flush, end=end)

def LevelInput(level:int, msg="", flush=False, end=''):
    LevelPrint(level,msg=msg,flush=flush,end=end)
    return input()

def AnyKeyDialog(msg=""):
    if msg != "":
        msg += " - "
    msg += "Press enter to continue..."
    input(msg)

def Clear():
    _os.system("cls" if _os.name == "nt" else "clear")
    return

def Prompt_YesOrNo(question:str) -> bool:
    '''
    prompts user indefinitely until one of the choices are picked

    output style: "<question> [Y/N]:"
    @return: boolean yes=True, no=False
    '''
    
    while(True):
        answer = input(question + " [Y/N]:").upper()
        if(answer == "Y"):
            return True
        elif(answer == "N"):
            return False

def Print_SelectFileDialog(message="Enter File Paths", indentLevel=0) -> list[str]|None:
    import shlex
    LevelPrint(indentLevel, f"-{message}")
    filepathString = LevelInput(indentLevel, "-")
    filepaths = shlex.split(filepathString)
    if(len(filepaths) == 0):
        return None
    return filepaths


class ConsoleSettingsManagerExtension():
    from simpleworkspace.settingsproviders import _SettingsManager_Base
    __Command_Delete = "#delete"

    def __init__(self, settingsManager: _SettingsManager_Base) -> None:
        self.SettingsManager = settingsManager
        

    def __Console_ChangeSettings(self):
        while True:
            Clear()
            LevelPrint(0, "[Change Settings]")
            LevelPrint(1, "0. Save Settings and go back.(Type cancel to discard changes)")
            LevelPrint(1, "1. Add a new setting")
            LevelPrint(2, "[Current Settings]")
            dictlist = []
            dictlist_start = 2
            dictlist_count = 2
            for key in self.SettingsManager.Settings:
                LevelPrint(3, str(dictlist_count) + ". " + key + " : " + str(self.SettingsManager.Settings[key]))
                dictlist.append(key)
                dictlist_count += 1
            LevelPrint(1)
            choice = input("-Choice: ")
            if choice == "cancel":
                self.SettingsManager.LoadSettings()
                AnyKeyDialog("Discarded changes!")
                break
            if choice == "0":
                self.SettingsManager.SaveSettings()
                LevelPrint(1)
                AnyKeyDialog("Saved Settings!")
                break
            elif choice == "1":
                LevelPrint(1, "Setting Name:")
                keyChoice = LevelInput(1, "-")
                LevelPrint(1, "Setting Value")
                valueChoice = LevelInput(1, "-")
                self.SettingsManager.Settings[keyChoice] = valueChoice
            else:
                IntChoice = None
                try:
                    IntChoice = int(choice)
                except Exception as e:
                    pass
                if IntChoice is None or (IntChoice >= dictlist_start and IntChoice < dictlist_count):
                    continue
                else:
                    key = dictlist[IntChoice - dictlist_start]
                    LevelPrint(2, '(Leave empty to cancel, or type "' + self.__Command_Delete + '" to remove setting)')
                    LevelPrint(2, ">> " + str(self.SettingsManager.Settings[key]))
                    choice = LevelInput(2, "Enter new value: ")
                    if choice == "":
                        continue
                    elif choice == self.__Command_Delete:
                        del self.SettingsManager.Settings[key]
                    else:
                        self.SettingsManager.Settings[key] = choice
        return

    def Console_PrintSettingsMenu(self):
        from simpleworkspace.io.path import PathInfo
        while(True):
            Clear()
            LevelPrint(0, "[Settings Menu]")
            LevelPrint(1, "1.Change settings")
            LevelPrint(1, "2.Reset settings")
            LevelPrint(1, "3.Open Settings Directory")
            LevelPrint(1, "0.Go back")
            LevelPrint(1)
            choice = input("-")
            if choice == "1":
                self.__Console_ChangeSettings()
            elif choice == "2":
                LevelPrint(1)
                confirmed = Prompt_YesOrNo("-Confirm Reset!")
                if confirmed:
                    self.SettingsManager.ClearSettings()
                    self.SettingsManager.SaveSettings()
                    LevelPrint(1)
                    AnyKeyDialog("*Settings resetted!")
            elif choice == "3":
                pathInfo = PathInfo(self.SettingsManager._settingsPath)
                _os.startfile(pathInfo.Tail)
            else:
                break
        return