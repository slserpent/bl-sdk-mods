import unrealsdk
from Mods.ModMenu import RegisterMod, SDKMod, Keybind, EnabledSaveType, Mods, ModTypes

class DayNight(SDKMod):
    Name: str = "Time of Day Changer"
    Author: str = "Snake"
    Description: str = (
        "Allows changing the current in-game time of day."
    )
    Version: str = "1.0"
    Types: ModTypes = ModTypes.Utility
    SaveEnabledState: EnabledSaveType = EnabledSaveType.LoadOnMainMenu
    
    TimeOfDay: float = 0.0

    Keybinds: list = [
        Keybind("Set Day", "F5"),
        Keybind("Set Night", "F6"),
        Keybind("Increment Time", "F7")
    ]

    def GameInputPressed(self, input):
        if input.Name == "Set Day" or input.Name == "Set Night" or input.Name == "Increment Time":
            if input.Name == "Set Day":
                self.TimeOfDay = 120.0
            if input.Name == "Set Night":
                self.TimeOfDay = 32.0
            if input.Name == "Increment Time":
                self.TimeOfDay += 1.0
                #time scale seems to be 0 to 200, so wrap around at 200
                if self.TimeOfDay > 199: self.TimeOfDay = 0.0
                
            daynight_seq: unrealsdk.UObject = unrealsdk.FindAll("WillowSeqAct_DayNightCycle")[0]
            daynight_seq.SetTimeOfDay(self.TimeOfDay)
            unrealsdk.Log(f"Time of day set to {self.TimeOfDay}")
        
mod_instance = DayNight()
# if __name__ == "__main__":
   # unrealsdk.Log(f"[{mod_instance.Name}] Manually loaded")
   # for mod in Mods:
       # if mod.Name == mod_instance.Name:
           # if mod.IsEnabled:
               # mod.Disable()
           # Mods.remove(mod)
           # unrealsdk.Log(f"[{mod_instance.Name}] Removed last instance")

           # # Fixes inspect.getfile()
           # mod_instance.__class__.__module__ = mod.__class__.__module__
           # break

RegisterMod(DayNight())