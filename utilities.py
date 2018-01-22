'''
Copyright (C) 2012 Brendan Scott

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/

Version info:
1.0beta 22 November 2012

'''



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
#        print d, scalingFactor, direction # wtf??
        
        return direction
    return g
 
