# pydefold-api



## Getting started

### Install  : 
```bash
pip install pydefoldapi
```
### Usage  : 
* Example 1: 
```python
from PyDefoldApi import DefoldApi 

c =DefoldApi.CollectionDesc(name = "main")
c.name  = "main"

o =DefoldApi.EmbeddedInstanceDesc(id = "go")

c.embedded_instances.append(o)
print(c.to_dict())
c.update({"name" : "ffffffff"})
print(c)

```

* Example 2: 
```python
from PyDefoldApi import DefoldApi 

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
```


