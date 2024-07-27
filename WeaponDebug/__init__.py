import unrealsdk
from Mods.ModMenu import RegisterMod, SDKMod, SaveModSettings, Options, Keybind, EnabledSaveType, Mods, ModTypes
from Mods.Enums import EModifierType

class WeaponDebug(SDKMod):
    Name: str = "Weapon Debug"
    Author: str = "Snake"
    Description: str = (
        "Adds on-screen real-time weapon statistics display."
    )
    Version: str = "1.0.1"
    Types: ModTypes = ModTypes.Utility
    SaveEnabledState: EnabledSaveType = EnabledSaveType.LoadOnMainMenu

    ShowStats: bool = True
    ShowParts: bool = True

    Keybinds: list = [
        Keybind("Toggle Stats", "F3"),
        Keybind("Toggle Parts", "F4")
    ]

    def __init__(self) -> None:
        self.Options = []
        self.ShowStatsDisplay = Options.Boolean (
            Caption="Show Stats Display",
            Description="Show Stats Display.",
            StartingValue=True,
            IsHidden=True
        )
        self.ShowPartsDisplay = Options.Boolean (
            Caption="Show Parts Display",
            Description="Show Parts Display.",
            StartingValue=True,
            IsHidden=True
        )
        self.RedSlider = Options.Slider (
            Caption="Red",
            Description="Red value for the text color.",
            StartingValue=255,
            MinValue=0,
            MaxValue=255,
            Increment=1,
            IsHidden=False
        )
        self.GreenSlider = Options.Slider (
            Caption="Green",
            Description="Green value for the text color.",
            StartingValue=170,
            MinValue=0,
            MaxValue=255,
            Increment=1,
            IsHidden=False
        )
        self.BlueSlider = Options.Slider (
            Caption="Blue",
            Description="Blue value for the text color.",
            StartingValue=0,
            MinValue=0,
            MaxValue=255,
            Increment=1,
            IsHidden=False
        )
        self.AlphaSlider = Options.Slider (
            Caption="Alpha",
            Description="Alpha value for the text color.",
            StartingValue=255,
            MinValue=0,
            MaxValue=255,
            Increment=1,
            IsHidden=False
        )
        self.TextColor = Options.Nested (
            Caption = "Text Color",
            Description="Text Color",
            Children = [self.RedSlider, self.GreenSlider, self.BlueSlider, self.AlphaSlider],
            IsHidden = False
        )

        self.SizeSlider = Options.Slider (
            Caption="Text Size",
            Description="Text scaling as a percentage.",
            StartingValue=80,
            MinValue=50,
            MaxValue=300,
            Increment=1,
            IsHidden=False
        )

        self.xPosSlider = Options.Slider (
            Caption="X Position",
            Description="X position as a percentage of the total screen.",
            StartingValue=1,
            MinValue=0,
            MaxValue=100,
            Increment=1,
            IsHidden=False
        )
        self.yPosSlider = Options.Slider (
            Caption="Y Position",
            Description="Y position as a percentage of the total screen.",
            StartingValue=1,
            MinValue=0,
            MaxValue=100,
            Increment=1,
            IsHidden=False
        )
        self.TextPos = Options.Nested (
            Caption = "Text Position",
            Description = "Text Position",
            Children = [self.xPosSlider, self.yPosSlider],
            IsHidden = False
        )

        self.Options = [
            self.TextColor,
            self.TextPos,
            self.SizeSlider,
            self.ShowStatsDisplay,
            self.ShowPartsDisplay
        ]
                
    def GameInputPressed(self, input):
        if input.Name == "Toggle Stats":
            self.ShowStats = not self.ShowStats
            self.ShowStatsDisplay.CurrentValue = self.ShowStats
        if input.Name == "Toggle Parts":
            self.ShowParts = not self.ShowParts
            self.ShowPartsDisplay.CurrentValue = self.ShowParts
        SaveModSettings(self)

    def Enable(self):
        def onPostRender(caller: unrealsdk.UObject, function: unrealsdk.UFunction, params: unrealsdk.FStruct) -> bool:
            self.displayDebug(params)
            return True

        unrealsdk.RegisterHook("WillowGame.WillowGameViewportClient.PostRender", "Postrender", onPostRender)
        self.ShowStats = self.ShowStatsDisplay.CurrentValue
        self.ShowParts = self.ShowPartsDisplay.CurrentValue

    def Disable(self):
        unrealsdk.RemoveHook("WillowGame.WillowGameViewportClient.PostRender", "Postrender")
        self.ShowStats = False
        self.ShowParts = False
                
                
    def eval_attr(self, attribute_name: str, get_base = False):
        attribute = unrealsdk.FindObject("AttributeDefinition", attribute_name)
        return self.eval_attr_obj(attribute, get_base)
        
    def eval_attr_obj(self, attribute: unrealsdk.UObject, get_base = False):
        context = unrealsdk.GetEngine().GamePlayers[0].Actor
        if get_base:
            return attribute.GetBaseValue(context)
        return attribute.GetValue(context)

    def displayDebug(self, params):
        if unrealsdk.GetEngine().GetCurrentWorldInfo().GetStreamingPersistentMapName().lower() == "menumap":
            return True
        if not params.Canvas:
            return True
                
        if self.ShowStats or self.ShowParts:
            part_info = ""
            stat_info = ""
            player_controller: unrealsdk.UObject = unrealsdk.GetEngine().GamePlayers[0].Actor
            current_weapon: unrealsdk.UObject = player_controller.Pawn.Weapon
            
            if self.ShowParts and current_weapon:
                #just make a little collection to simplify the access to the per-grade data
                attrib_grades = {}
                for attribute in current_weapon.DefinitionData.WeaponTypeDefinition.AttributeSlotEffects:
                    attrib_grades[attribute.SlotName] = attribute.PerGradeUpgrade.BaseValueConstant
                
                weapon_parts = ["WeaponTypeDefinition", "BarrelPartDefinition", "GripPartDefinition", "BodyPartDefinition", "StockPartDefinition", "SightPartDefinition", "ElementalPartDefinition", "Accessory1PartDefinition", "Accessory2PartDefinition"]
                attribute_effects = ["WeaponAttributeEffects", "ExternalAttributeEffects", "ZoomWeaponAttributeEffects", "ZoomExternalAttributeEffects"]
                for part_def in weapon_parts:
                    part = getattr(current_weapon.DefinitionData, part_def)
                    if part is None:
                        continue
                    for effect_type in attribute_effects:
                        effect = getattr(part, effect_type)
                        if effect is None:
                            continue
                        for attrib in effect:
                            #check for a disabled element
                            if attrib is None or attrib.AttributeToModify is None:
                                continue
                            attrib_value = 0
                            if attrib.BaseModifierValue.BaseValueAttribute is None:
                                attrib_value = attrib.BaseModifierValue.BaseValueConstant * attrib.BaseModifierValue.BaseValueScaleConstant
                            else:
                                attrib_value = attrib.BaseModifierValue.BaseValueScaleConstant
                                attrib_attrib, resolved_context = self.eval_attr_obj(attrib.BaseModifierValue.BaseValueAttribute)
                                #if the context resolver resolves to false, then skip this attribute
                                if attrib_attrib == 0:
                                    continue
                            
                            #if the value is 0 (unchanged), then skip this attribute
                            if attrib_value == 0:
                                continue 
                                
                            if attrib.ModifierType == EModifierType.MT_Scale:
                                if attrib_value > 0:
                                    attrib_value = (1 + attrib_value) / 1
                                else:
                                    attrib_value = 1 / (1 + abs(attrib_value))
                                attrib_value = "x" + str(round(attrib_value, 2))
                            else:
                                if attrib_value > 0:
                                    attrib_value = "+" + str(round(attrib_value, 2))
                                else:
                                    attrib_value = "-" + str(round(abs(attrib_value), 2))
                            
                            if effect_type == "ZoomWeaponAttributeEffects" or effect_type == "ZoomExternalAttributeEffects":
                                attrib_value += " (zoom)"
                                
                            part_info += f" {part.Name}: {attrib.AttributeToModify.Name} {attrib_value}\n"
                    for attrib_upgrade in part.AttributeSlotUpgrades:
                        attrib_value = attrib_grades[attrib_upgrade.SlotName] * attrib_upgrade.GradeIncrease
                        if attrib_value > 0:
                            attrib_value = "+" + str(round(attrib_value, 2))
                        elif attrib_value == 0:
                            #if the value is 0 (unchanged), then skip this attribute
                            continue
                        else:
                            attrib_value = "-" + str(round(abs(attrib_value), 2))
                        part_info += f" {part.Name}: {attrib_upgrade.SlotName} {attrib_value} ({attrib_upgrade.GradeIncrease}grd)\n"

            if self.ShowStats:
                spread, resolved_context = self.eval_attr("D_Attributes.Weapon.WeaponSpread")
                spread_base, resolved_context = self.eval_attr("D_Attributes.Weapon.WeaponSpread", True)
                kick, resolved_context = self.eval_attr("D_Attributes.Weapon.WeaponPerShotAccuracyImpulse")
                kick_base, resolved_context = self.eval_attr("D_Attributes.Weapon.WeaponPerShotAccuracyImpulse", True)
                burst_kick, resolved_context = self.eval_attr("D_Attributes.Weapon.WeaponBurstShotAccuracyImpulseScale")
                burst_kick_base, resolved_context = self.eval_attr("D_Attributes.Weapon.WeaponBurstShotAccuracyImpulseScale", True)
                sway_regen_base, resolved_context = self.eval_attr("D_Attributes.AccuracyResourcePool.AccuracyOnIdleRegenerationRate")
                damage, resolved_context = self.eval_attr("D_Attributes.Weapon.WeaponDamage")
                
                sway = player_controller.AccuracyPool.Data.GetCurrentValue()
                min_sway = player_controller.AccuracyPool.Data.GetMinValue()
                max_sway = player_controller.AccuracyPool.Data.GetMaxValue()
                sway_regen = player_controller.AccuracyPool.Data.GetTotalRegenRate()
                
                if current_weapon:
                    spread_def = current_weapon.DefinitionData.WeaponTypeDefinition.Spread
                    kick_def = current_weapon.DefinitionData.WeaponTypeDefinition.PerShotAccuracyImpulse
                    burst_kick_def = current_weapon.DefinitionData.WeaponTypeDefinition.BurstShotAccuracyImpulseScale
                    kick_speed = current_weapon.DefinitionData.WeaponTypeDefinition.WeaponKickSpeed
                    kick_recovery = current_weapon.DefinitionData.WeaponTypeDefinition.WeaponKickRecoveryTime
                    kick_zoom_mult = current_weapon.DefinitionData.WeaponTypeDefinition.WeaponKickZoomMultiplier
                else:
                    spread_def = 0.0
                    kick_def = 0.0
                    burst_kick_def = 0.0
                    kick_speed = 0.0
                    kick_recovery = 0.0
                    kick_zoom_mult = 0.0
                    
                stat_info = f" Spread: {spread:.2f} ({spread_base:.2f}, {spread_def:.2f})\n Kick: {kick:.2f} ({kick_base:.2f}, {kick_def:.2f})\n Burst Kick: {burst_kick:.2f} ({burst_kick_base:.2f}, {burst_kick_def:.2f})\n Sway: {sway:.2f}\n Sway Regen: {sway_regen:.2f}, {sway_regen_base:.2f}\n Min Sway: {min_sway:.2f}\n Max Sway: {max_sway:.2f}\n Kick Speed: {kick_speed:.2f}\n Kick Recovery: {kick_recovery:.2f}\n Kick Zoom Mult: {kick_zoom_mult:.2f}\n Damage: {damage:.0f} "
                    
            canvas = params.Canvas
            FontRenderInfo = (False, True)
            canvas.Font = unrealsdk.FindObject("Font", "UI_Fonts.Font_Willowbody_18pt")
            
            scalex = self.SizeSlider.CurrentValue / 100
            scaley = self.SizeSlider.CurrentValue / 100
            trueX = canvas.SizeX * (self.xPosSlider.CurrentValue / 100)
            trueY = canvas.SizeX * (self.yPosSlider.CurrentValue / 100)

            canvas.SetPos(trueX, trueY, 0)
            
            color = (self.BlueSlider.CurrentValue, self.GreenSlider.CurrentValue, self.RedSlider.CurrentValue, self.AlphaSlider.CurrentValue)
            try:
                canvas.SetDrawColorStruct(color) #b, g, r, a
            except:
                pass
            
            if len(part_info) > 0 and len(stat_info) > 0:
                text = part_info + "\n" + stat_info
            else:
                text = part_info + stat_info
                
            canvas.DrawText(text, False, scalex, scaley, FontRenderInfo)
        return True
        
mod_instance = WeaponDebug()
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

RegisterMod(WeaponDebug())