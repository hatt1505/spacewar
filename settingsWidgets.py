import SFsettings

################
#
#  Space Fighto! Settings 
#
###############

gravityScale = SFsettings.individualSetting(
            label = "Gravity Strength",  
            id = "gravityScale",  
            widgetType = SFsettings.FLOATWIDGET,  
            rangeStart= -10.0,  rangeEnd= 10.0,  
            valueList = [],
            descriptionList = [], 
            fpDescriptionList=[(-11,  "Madness!"), ( -8.1, "Extremely Repulsive"), (-6.1, "Pretty Repulsive"), 
                               (-3.1, "Oppositional"), 
                               (-1, "AntiGravity!"), (0.0, "Very Weak"), (0.5, "Weak"), (0.75, "Normal"), 
                               (3.0, "Strong"), 
                               (6.0, "Very Strong"),
                             (8.0, "A bit much"), 
                               (9.5, "Are You Insane?")], 
            defaultValue = 1.0
            )

bulletSpeed = SFsettings.individualSetting(
            label = "Bullet Speed",  
            id = "bulletSpeed",  
            widgetType = SFsettings.FLOATWIDGET,  
            rangeStart= 0.1,  rangeEnd= 10.0,  
            valueList = [],
            descriptionList = [], 
            fpDescriptionList=[(-1, "Soporific"), (0.4, "Slooooowwww"), (0.7, "Slowish"), (0.99, "Normal"), 
                               (3.0, "Fast"), (6.0, "Very Fast"),  
                               (8.0,  "Steady on..."), 
                               (9.5, "Are You Insane?")], 
            defaultValue = 1.0
            )

bulletLife = SFsettings.individualSetting(
            label = "Bullet Life",  
            id = "bulletLife",  
            widgetType = SFsettings.FLOATWIDGET,  
            rangeStart= 0.1,  rangeEnd= 10.0,  
            valueList = [],
            descriptionList = [], 
            fpDescriptionList=[(-1, "Good Luck!"), (0.4, "Very Short"), (0.7, "Youngish"), (0.99, "Normal"), 
                               (3.0, "Long lived"), (6.0, "Very Old"),  
                               (8.0,  "Antique"), 
                               (9.5, "Ancient")], 
            defaultValue = 1.0
            )


thrusterPower=  SFsettings.individualSetting(
            label = "Thruster Power",  
            id = "thrusterMultiplier",  
            widgetType = SFsettings.FLOATWIDGET,  
            rangeStart= 0.1,  rangeEnd= 10.0,  
            valueList = [],
            descriptionList = [], 
            fpDescriptionList=[(-1, "Pathetic"), (0.4, "Very Weak"), (0.7, "Weak"), (0.99, "Normal"), 
                               (3.0, "Strong"), (6.0, "Trapped Fly"),  
                               (8.0,  "Ridiculous"), 
                               (9.5, "Are You Insane?")], 
            defaultValue = 1.0
            ) 

settingsList = [gravityScale,  bulletSpeed, bulletLife, thrusterPower]
