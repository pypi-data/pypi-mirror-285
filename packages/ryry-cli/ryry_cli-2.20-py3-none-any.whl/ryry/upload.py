from urllib.parse import *

def addtionExif(srcFile, taskUUID):
    if taskUUID == None or len(taskUUID) == 0:
        return
    try:
        from pathlib import Path
        file_name = Path(srcFile).name
        ext = file_name[file_name.index("."):].lower()
        if ext in [".jpg", ".png", ".jpeg", ".bmp", ".webp", ".gif"]:
            from PIL import Image
            img = Image.open(srcFile)
            exif_dict = {
                "0th": { }, 
                "Exif": { }, 
                "1st": { },
                "thumbnail": None, 
                "GPS": { }
            }
            import piexif
            if taskUUID:
                exif_dict["0th"] = { 
                    piexif.ImageIFD.Software: f'make with ryry({taskUUID})'.encode(),
                    piexif.ImageIFD.Copyright: f'dalipen'.encode(),
                }
                exif_dict["Exif"] = {
                    piexif.ExifIFD.UserComment: f'make with ryry({taskUUID})'.encode(),
                }
            exif_dat = piexif.dump(exif_dict)
            img.save(srcFile, "webp", quality=90, exif=exif_dat)
        # elif ext in [".mp4",".mov",".avi",".wmv",".mpg",".mpeg",".rm",".ram",".flv",".swf",".ts"]:
        #     params = {}
        # elif ext in [".mp3",".aac",".wav",".wma",".cda",".flac",".m4a",".mid",".mka",".mp2",".mpa",".mpc",".ape",".ofr",".ogg",".ra",".wv",".tta",".ac3",".dts"]:
        #     params = {}
        # else:
        #     params = {}
    except:
        return

def transcode(srcFile):
    try:
        from pathlib import Path
        from PIL import Image
        file_name = Path(srcFile).name
        ext = file_name[file_name.index("."):].lower()
        if ext in [".jpg", ".png", ".jpeg", ".bmp"]:
            image = Image.open(srcFile, "r")
            format = image.format
            if format.lower() != "webp":
                fname = Path(srcFile).name
                newFile = srcFile.replace(fname[fname.index("."):], ".webp")
                image.save(newFile, "webp", quality=90)
                image.close()
                return True, newFile
    except Exception as e:
        pass
    return False, srcFile

def additionalUrl(srcFile, ossUrl):
    from pathlib import Path
    from PIL import Image
    try:
        file_name = Path(srcFile).name
        ext = file_name[file_name.index("."):].lower()
        params = {}
        if ext in [".jpg", ".png", ".jpeg", ".bmp", ".webp", ".gif"]:
            img = Image.open(srcFile)
            params["width"] = img.width
            params["height"] = img.height
        elif ext in [".mp4",".mov",".avi",".wmv",".mpg",".mpeg",".rm",".ram",".flv",".swf",".ts"]:
            params = {}
        elif ext in [".mp3",".aac",".wav",".wma",".cda",".flac",".m4a",".mid",".mka",".mp2",".mpa",".mpc",".ape",".ofr",".ogg",".ra",".wv",".tta",".ac3",".dts"]:
            params = {}
        else:
            params = {}
        parsed_url = urlparse(ossUrl)
        updated_query_string = urlencode(params, doseq=True)
        final_url = parsed_url._replace(query=updated_query_string).geturl()
        return final_url
    except:
        return ossUrl

def upload(src, taskUUID, timeout=300, needTranscode=True):
    import os
    from ryry import store
    from pathlib import Path
    from ryry import taskUtils
    from ryry import ryry_webapi
    import requests
    if os.path.exists(src) == False:
        raise Exception(f"upload file not found")
    if taskUUID==None or len(taskUUID) <= 0:
        taskUUID = taskUtils.taskInfoWithFirstTask()

    if needTranscode:
        needDeleteSrc, newSrc = transcode(src)
    else:
        needDeleteSrc = False
        newSrc = src
    addtionExif(newSrc, taskUUID)
    file_name = Path(newSrc).name
    ossurl = ryry_webapi.upload(newSrc, os.path.splitext(file_name)[-1][1:])
    ossurl = additionalUrl(newSrc, ossurl)
    if needDeleteSrc:
        os.remove(newSrc)
    return ossurl