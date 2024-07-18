from  PyDefold import Defold
from PyDefoldApi import DefoldApi

def test_import() : 
    camera = Defold.CameraDesc()
    camera.fov = 150
    print(camera)
    cam = Defold.CameraDesc(**{
        "aspect_ratio": 0.0,
        "fov": 150,
        "near_z":15,
        "far_z": 0.0,
        "auto_aspect_ratio": 0,
        "orthographic_projection": 0,
        "orthographic_zoom": 1.0
    })
    print(cam.type)

    v = Defold.QVelocityResponse()
    print(v.fields)
    print(v.to_dict())
    print(v.to_proto(file = "here.proto"))
    return True


def test_PyDefoldApi_import(self) : 
    cam = DefoldApi.CameraDesc()
    cam.update({
        "aspect_ratio": 0.0,
        "fov": 150,
        "near_z":15,
        "far_z": 0.0,
        "auto_aspect_ratio": 0,
        "orthographic_projection": 0,
        "orthographic_zoom": 1.0
    })
    print(cam.to_dict())
    return True 



def test_collection() : 
    c =DefoldApi.CollectionDesc(name = "main")
    c.name  = "main"
    o =DefoldApi.EmbeddedInstanceDesc(id = "go")
    print(c.__optional_defaults__)
    c.embedded_instances.append(o)
    print(c.to_dict())
    c.update({"name" : "ffffffff"})
    print(c)
    return True 