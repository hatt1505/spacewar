from constants import *
FPERROR = 1E-5

def gravityFactory(towards=SCREEN_CENTRE, 
                   strength=10.0,  
                   gravityScale = 1.0, 
#                   strength= 0.0,  
                   unitDistanceInPixels = 600.0, power =2.0):
    scalingLimit =1200
    def g(p):
        if abs(gravityScale) <FPERROR:  # just dealing with floating point errors to ensure really zero gravity
            return (0, 0) # no gravity
        direction = towards-p
        d = direction.get_length()/unitDistanceInPixels
        scalingFactor = strength*gravityScale/(d**power)
        if scalingFactor > scalingLimit:
            scalingFactor = scalingLimit

        direction = direction.normalized()*scalingFactor
        
        return direction
    return g
