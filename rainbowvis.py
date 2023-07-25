import math
import re
import sys

class Rainbow:
    def __init__(self):
        self.gradients = [];
        self.minNum = 0
        self.maxNum = 100
        self.colours = ['ff0000', 'ffff00', '00ff00', '0000ff'] 
        self.setColours(self.colours)
    
    def setColours(self, spectrum): 
    
        if len(spectrum) < 2:
            raise Exception('Rainbow must have two or more colours.')
        else:
            increment = (self.maxNum - self.minNum)/(len(spectrum) - 1)
            firstGradient = ColourGradient()
            firstGradient.setGradient(spectrum[0], spectrum[1])
            firstGradient.setNumberRange(self.minNum, self.minNum + increment)
            
            
            self.gradients = [ None ] * (len(spectrum) -1)
            self.gradients[0] =  firstGradient 
            
            for i in range(1,len(spectrum)-1):
                colourGradient = ColourGradient()
                colourGradient.setGradient(spectrum[i], spectrum[i + 1])
                colourGradient.setNumberRange(self.minNum + increment * i, self.minNum + increment * (i + 1)) 
                self.gradients[i] = colourGradient 

            self.colours = spectrum

    def setSpectrum(self, *arguments): 
        self.setColours(arguments)
        return self

    def setSpectrumByArray(self, array):
        self.setColours(array)
        return self
    

    def colourAt(self, number):
 
    
        if math.isnan(number):
            raise Exception("%d is not a number" % number)
        elif len(self.gradients) == 1:
            return self.gradients[0].colourAt(number)
        else:
            
            segment = (self.maxNum - self.minNum)/float(len(self.gradients))
            index = min(math.floor((max(number, self.minNum) - self.minNum)/segment), len(self.gradients) - 1)
            

            
            index = int(index)
            return self.gradients[index].colourAt(number);
        
    
    def colorAt(self, number): return self.colourAt(number)

    def setNumberRange(self, minNumber, maxNumber):
        if maxNumber > minNumber:
            self.minNum = minNumber
            self.maxNum = maxNumber
            self.setColours(self.colours)
        else:
            raise Exception("maxNumber ('%d') is not greater than minNumber ('%d')" % ( maxNumber, minNumber) )
        return self


class ColourGradient:
    def __init__(self):
        self.startColour = 'ff0000'
        self.endColour = '0000ff'
        self.minNum = 0
        self.maxNum = 100

         #Extended list of CSS colornames s taken from
        # http://www.w3.org/TR/css3-color/#svg-color
        self.colourNames = {
            'aliceblue': "F0F8FF",
            'antiquewhite': "FAEBD7",
            'aqua': "00FFFF",
            'aquamarine': "7FFFD4",
            'azure': "F0FFFF",
            'beige': "F5F5DC",
            'bisque': "FFE4C4",
            'black': "000000",
            'blanchedalmond': "FFEBCD",
            'blue': "0000FF",
            'blueviolet': "8A2BE2",
            'brown': "A52A2A",
            'burlywood': "DEB887",
            'cadetblue': "5F9EA0",
            'chartreuse': "7FFF00",
            'chocolate': "D2691E",
            'coral': "FF7F50",
            'cornflowerblue': "6495ED",
            'cornsilk': "FFF8DC",
            'crimson': "DC143C",
            'cyan': "00FFFF",
            'darkblue': "00008B",
            'darkcyan': "008B8B",
            'darkgoldenrod': "B8860B",
            'darkgray': "A9A9A9",
            'darkgreen': "006400",
            'darkgrey': "A9A9A9",
            'darkkhaki': "BDB76B",
            'darkmagenta': "8B008B",
            'darkolivegreen': "556B2F",
            'darkorange': "FF8C00",
            'darkorchid': "9932CC",
            'darkred': "8B0000",
            'darksalmon': "E9967A",
            'darkseagreen': "8FBC8F",
            'darkslateblue': "483D8B",
            'darkslategray': "2F4F4F",
            'darkslategrey': "2F4F4F",
            'darkturquoise': "00CED1",
            'darkviolet': "9400D3",
            'deeppink': "FF1493",
            'deepskyblue': "00BFFF",
            'dimgray': "696969",
            'dimgrey': "696969",
            'dodgerblue': "1E90FF",
            'firebrick': "B22222",
            'floralwhite': "FFFAF0",
            'forestgreen': "228B22",
            'fuchsia': "FF00FF",
            'gainsboro': "DCDCDC",
            'ghostwhite': "F8F8FF",
            'gold': "FFD700",
            'goldenrod': "DAA520",
            'gray': "808080",
            'green': "008000",
            'greenyellow': "ADFF2F",
            'grey': "808080",
            'honeydew': "F0FFF0",
            'hotpink': "FF69B4",
            'indianred': "CD5C5C",
            'indigo': "4B0082",
            'ivory': "FFFFF0",
            'khaki': "F0E68C",
            'lavender': "E6E6FA",
            'lavenderblush': "FFF0F5",
            'lawngreen': "7CFC00",
            'lemonchiffon': "FFFACD",
            'lightblue': "ADD8E6",
            'lightcoral': "F08080",
            'lightcyan': "E0FFFF",
            'lightgoldenrodyellow': "FAFAD2",
            'lightgray': "D3D3D3",
            'lightgreen': "90EE90",
            'lightgrey': "D3D3D3",
            'lightpink': "FFB6C1",
            'lightsalmon': "FFA07A",
            'lightseagreen': "20B2AA",
            'lightskyblue': "87CEFA",
            'lightslategray': "778899",
            'lightslategrey': "778899",
            'lightsteelblue': "B0C4DE",
            'lightyellow': "FFFFE0",
            'lime': "00FF00",
            'limegreen': "32CD32",
            'linen': "FAF0E6",
            'magenta': "FF00FF",
            'maroon': "800000",
            'mediumaquamarine': "66CDAA",
            'mediumblue': "0000CD",
            'mediumorchid': "BA55D3",
            'mediumpurple': "9370DB",
            'mediumseagreen': "3CB371",
            'mediumslateblue': "7B68EE",
            'mediumspringgreen': "00FA9A",
            'mediumturquoise': "48D1CC",
            'mediumvioletred': "C71585",
            'midnightblue': "191970",
            'mintcream': "F5FFFA",
            'mistyrose': "FFE4E1",
            'moccasin': "FFE4B5",
            'navajowhite': "FFDEAD",
            'navy': "000080",
            'oldlace': "FDF5E6",
            'olive': "808000",
            'olivedrab': "6B8E23",
            'orange': "FFA500",
            'orangered': "FF4500",
            'orchid': "DA70D6",
            'palegoldenrod': "EEE8AA",
            'palegreen': "98FB98",
            'paleturquoise': "AFEEEE",
            'palevioletred': "DB7093",
            'papayawhip': "FFEFD5",
            'peachpuff': "FFDAB9",
            'peru': "CD853F",
            'pink': "FFC0CB",
            'plum': "DDA0DD",
            'powderblue': "B0E0E6",
            'purple': "800080",
            'red': "FF0000",
            'rosybrown': "BC8F8F",
            'royalblue': "4169E1",
            'saddlebrown': "8B4513",
            'salmon': "FA8072",
            'sandybrown': "F4A460",
            'seagreen': "2E8B57",
            'seashell': "FFF5EE",
            'sienna': "A0522D",
            'silver': "C0C0C0",
            'skyblue': "87CEEB",
            'slateblue': "6A5ACD",
            'slategray': "708090",
            'slategrey': "708090",
            'snow': "FFFAFA",
            'springgreen': "00FF7F",
            'steelblue': "4682B4",
            'tan': "D2B48C",
            'teal': "008080",
            'thistle': "D8BFD8",
            'tomato': "FF6347",
            'turquoise': "40E0D0",
            'violet': "EE82EE",
            'wheat': "F5DEB3",
            'white': "FFFFFF",
            'whitesmoke': "F5F5F5",
            'yellow': "FFFF00",
            'yellowgreen': "9ACD32"
        }


    def setGradient(self, colourStart, colourEnd):
        self.startColour = self.getHexColour(colourStart)
        self.endColour = self.getHexColour(colourEnd)
    
    
    def setNumberRange(self, minNumber, maxNumber):
        if maxNumber > minNumber:
            self.minNum = minNumber
            self.maxNum = maxNumber
        else:
            raise Exception("maxNumber ('%d') is not greater than minNumber ('%d')" % ( maxNumber, minNumber) )
        
    
    def colourAt(self, number):
        
        r = self.calcHex(number, self.startColour[0:2],  self.endColour[0:2])
        g = self.calcHex(number,  self.startColour[2:4],  self.endColour[2:4])
        b = self.calcHex(number,  self.startColour[4:6],  self.endColour[4:6])
        
        v = "%s%s%s" % (r,g,b)
              
        return v
               
    
    def calcHex(self, number, channelStart_Base16, channelEnd_Base16):

        num = number
        if num <  self.minNum:
            num =  self.minNum

        if num >  self.maxNum:
            num =  self.maxNum

        numRange =  self.maxNum -  self.minNum
        
        
        cStart_Base10 = int(channelStart_Base16, 16);
        cEnd_Base10 = int(channelEnd_Base16, 16);
        
         
        cPerUnit = (cEnd_Base10 - cStart_Base10)/numRange;
        c_Base10 = round(cPerUnit * (num -  self.minNum) + cStart_Base10);
        
        return self.formatHex("%x" % int(math.fabs(c_Base10))) # 16
    

    def formatHex(self,hexv): 
        if len(hexv) == 1:
            return '0' + hexv;
        else:
            return hexv
    
    def isHexColour(self,string):
        regstr = "^#?[0-9a-fA-F]{6}$";
        x = re.match(regstr, string)
        if x: return True
        return False

    
    def getHexColour(self,string):
        
        if self.isHexColour(string):
            
            return string[len(string) - 6: len(string)]
            
        else:
            name = string.lower()
            if name in list(self.colourNames.keys()): 
                return self.colourNames[name]
            raise Exception("%s is not a valid colour." % string)
    
    
def SlopeGradient():
    rainbow = Rainbow()
    #see http://www.colorzilla.com/gradient-editor/
    #rainbow.setSpectrum('#0000D0','#00C000', '#FF0000')
    #rainbow.setSpectrum('#0300B7','#00E5A8', '#79D600', '#D80000')
    rainbow.setSpectrum('#030057','#0300B7','#0095B8', '#00D0A0', '#79E600','#D83000', '#582010')
    rainbow.setNumberRange(-20, 20); 
    return rainbow

if __name__ == "__main__":
    
    rainbow = SlopeGradient()
    
    for i in range(-20,20):
        color = rainbow.colourAt(i + 0.1);
        print("<span style='background-color: #%s;'>%d -> %s</span></br>\n" % (color, i, color))

    