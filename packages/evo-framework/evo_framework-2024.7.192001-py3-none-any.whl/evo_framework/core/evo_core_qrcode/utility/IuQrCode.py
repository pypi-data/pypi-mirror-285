#========================================================================================================================================
# CyborgAI CC BY-NC-ND 4.0 Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 Internation    https://github.com/cyborg-ai-git |
#========================================================================================================================================
from evo_framework.core.evo_core_log.utility.IuLog import IuLog

from PIL import Image, ImageDraw, ImageFilter
import qrcode
import asyncio

class IuQrCode:
    
    @staticmethod
    async def doPrintAscii(strQrcode: str, isInvert=False ):
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
          

            qr.add_data(f"{strQrcode}")
            qr.make(fit=True)
            if isInvert:
                qr.print_ascii(tty=True, invert=True)
            else:    
                qr.print_ascii()
           
            
        except Exception as exception:
            IuLog.doException(__name__, exception)
            raise Exception
    
    
    @staticmethod
    async def doGenerate(strQrcode: str, pathSave:str = None, pathLogo:str = None):
        try:
            
            await IuQrCode.doPrintAscii(strQrcode)
           
            #print(pathSave)
            if (pathSave is not None):
                
                if (pathLogo is not None):
                    await IuQrCode.doGenerateImage(strQrcode, pathSave, pathLogo)
                else:
                
                    imageQrCode = qrcode.make(f"{strQrcode}")
                    imageQrCode.save(pathSave)
            
            
        except Exception as exception:
            IuLog.doException(__name__, exception)
            raise Exception

    @staticmethod
    async def doGenerateImage(strQrcode: str, pathSave:str = None, pathLogo:str = None):
        # strQrcode="http://cyborgai.fly.dev"
        try:
            
            logo = Image.open(pathLogo)
            basewidth = 100
            wpercent = (basewidth / float(logo.size[0]))
            hsize = int((float(logo.size[1]) * float(wpercent)))
            logo = logo.resize((basewidth, hsize), Image.LANCZOS)

            # Assuming the logo has an alpha channel, apply a blur to the alpha channel for smoother edges
            if logo.mode in ('RGBA', 'LA') or (logo.mode == 'P' and 'transparency' in logo.info):
                alpha = logo.getchannel('A')
                blurred_alpha = alpha.filter(ImageFilter.GaussianBlur(radius=1))  # Adjust blur radius as needed
                logo.putalpha(blurred_alpha)

            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(strQrcode)
            qr.make(fit=True)

            qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

            pos = ((qr_img.size[0] - logo.size[0]) // 2, (qr_img.size[1] - logo.size[1]) // 2)
            qr_img.paste(logo, pos, logo)

            qr_img.save(pathSave)
                            
        except Exception as exception:
            IuLog.doException(__name__, exception)
            raise Exception

