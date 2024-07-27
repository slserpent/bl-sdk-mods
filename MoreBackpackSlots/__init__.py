import unrealsdk
from Mods.ModMenu import RegisterMod, SDKMod, Options, EnabledSaveType, Mods, ModTypes

class MoreBackpackSlots(SDKMod):
    Name: str = "More Backpack Slots"
    Author: str = "Snake"
    Description: str = (
        "Gives more backpack slots for each black market upgrade level. The amount of slots is selected in the mod options, but can only take affect after reloading from the main menu. This mod does not modify savegames."
    )
    Version: str = "1.0"
    Types: ModTypes = ModTypes.Gameplay
    SaveEnabledState: EnabledSaveType = EnabledSaveType.LoadOnMainMenu
    
    def __init__(self) -> None:
        self.Options = []
        self.SlotsPerUpgrade = Options.Slider (
            Caption="Backpack Slots Per Upgrade",
            Description="The number of backpack slots each black market upgrade gives. Requires a reload before taking effect.",
            StartingValue=6,
            MinValue=3,
            MaxValue=12,
            Increment=1,
            IsHidden=False
        )
        
        self.Options = [
            self.SlotsPerUpgrade
        ]
        
    def Enable(self) -> None:
        def ApplyInventorySaveGameData(caller: unrealsdk.UObject, function: unrealsdk.UFunction, params: unrealsdk.FStruct) -> bool:
            inv_manager = caller.GetPawnInventoryManager()
            if inv_manager:
                # the maximum backpack slots by default are 39. 12+(3*9)
                # this code increases that by overwriting the value of the backpack size during savegame load
                # it is calculated as [base inventory size] + ([stored backpack upgrade level] * [user-selected slots per upgrade level])
                inv_manager.InventorySlotMax_Misc = 12 + (params.SaveGame.BlackMarketUpgrades[7] * self.SlotsPerUpgrade.CurrentValue)
                
                if inv_manager.InventorySlotMax_Misc != 12 + (params.SaveGame.BlackMarketUpgrades[7] * self.SlotsPerUpgrade.CurrentValue):
                    unrealsdk.Log(f"Failed to set new value for total backpack upgrade slots.")
            else:
                unrealsdk.Log(f"Unable to get inventory manager.")
            
            # this code sets the amount of slots per upgrade for the black market UI
            # it seems unaffected by the 39 slots limit on backpack size, as that is only applied during loads from the menu
            attribute = unrealsdk.FindObject("ConstantAttributeValueResolver", "GD_BlackMarket.Misc.Att_BackPackSlotsPerUpgrade:ConstantAttributeValueResolver_0")
            if attribute:
                attribute.ConstantValue = self.SlotsPerUpgrade.CurrentValue
                
                if attribute.ConstantValue != self.SlotsPerUpgrade.CurrentValue:
                    unrealsdk.Log(f"Failed to set new value for black market backpack upgrade slots.")
            else:
                unrealsdk.Log(f"Unable to get object for black market backpack upgrade slots.")

            return True
            
        unrealsdk.RegisterHook("WillowGame.WillowPlayerController.ApplyInventorySaveGameData", "ApplyInventorySaveGameData", ApplyInventorySaveGameData)

    def Disable(self) -> None:
        unrealsdk.RemoveHook("WillowGame.WillowPlayerController.ApplyInventorySaveGameData", "ApplyInventorySaveGameData")
        
mod_instance = MoreBackpackSlots()
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

RegisterMod(MoreBackpackSlots())