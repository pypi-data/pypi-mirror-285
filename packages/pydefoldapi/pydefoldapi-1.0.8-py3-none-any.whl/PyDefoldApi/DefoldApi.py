
import json , os , sys , collections
from  google.protobuf.text_format import  Parse , MessageToString
from google.protobuf.json_format import MessageToDict , MessageToJson , ParseDict
from PyDefold import Defold 
DefoldApi = dict()



class Matrix4:
	__required__ = ["m00", "m01", "m02", "m03", "m10", "m11", "m12", "m13", "m20", "m21", "m22", "m23", "m30", "m31", "m32", "m33"]
	__optional__ = []
	__required_types__ = ["float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.m00 = 1.0
		self.m01 = 0.0
		self.m02 = 0.0
		self.m03 = 0.0
		self.m10 = 0.0
		self.m11 = 1.0
		self.m12 = 0.0
		self.m13 = 0.0
		self.m20 = 0.0
		self.m21 = 0.0
		self.m22 = 1.0
		self.m23 = 0.0
		self.m30 = 0.0
		self.m31 = 0.0
		self.m32 = 0.0
		self.m33 = 1.0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['Matrix4'] = Matrix4
		
		


class Point3:
	__required__ = ["x", "y", "z", "d"]
	__optional__ = []
	__required_types__ = ["float", "float", "float", "float"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.x = 0.0
		self.y = 0.0
		self.z = 0.0
		self.d = 0.0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['Point3'] = Point3
		
		


class Quat:
	__required__ = ["x", "y", "z", "w"]
	__optional__ = []
	__required_types__ = ["float", "float", "float", "float"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.x = 0.0
		self.y = 0.0
		self.z = 0.0
		self.w = 1.0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['Quat'] = Quat
		
		


class Transform:
	__required__ = ["rotation", "translation", "scale"]
	__optional__ = []
	__required_types__ = ["Quat", "Vector3", "Vector3"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.rotation = Quat()
		self.translation = Vector3()
		self.scale = Vector3()
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['Transform'] = Transform
		
		


class Vector3:
	__required__ = ["x", "y", "z", "d"]
	__optional__ = []
	__required_types__ = ["float", "float", "float", "float"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.x = 0.0
		self.y = 0.0
		self.z = 0.0
		self.d = 0.0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['Vector3'] = Vector3
		
		


class Vector4:
	__required__ = ["x", "y", "z", "w"]
	__optional__ = []
	__required_types__ = ["float", "float", "float", "float"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.x = 0.0
		self.y = 0.0
		self.z = 0.0
		self.w = 0.0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['Vector4'] = Vector4
		
		


class HideApp:
	__required__ = []
	__optional__ = []
	__required_types__ = []
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['HideApp'] = HideApp
		
		


class RunScript:
	__required__ = ["module"]
	__optional__ = []
	__required_types__ = ["LuaModule"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.module = LuaModule()
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['RunScript'] = RunScript
		
		


class AcquireInputFocus:
	__required__ = []
	__optional__ = []
	__required_types__ = []
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['AcquireInputFocus'] = AcquireInputFocus
		
		


class CollectionDesc:
	__required__ = ["name", "scale_along_z"]
	__optional__ = ["instances", "collection_instances", "embedded_instances", "property_resources", "component_types"]
	__required_types__ = ["string", "uint32"]
	__optional_types__ = ["InstanceDesc", "CollectionInstanceDesc", "EmbeddedInstanceDesc", "string", "ComponenTypeDesc"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"instances": [], "collection_instances": [], "embedded_instances": [], "property_resources": [], "component_types": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.name = ""
		self.scale_along_z = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['CollectionDesc'] = CollectionDesc
		
		


class CollectionInstanceDesc:
	__required__ = ["id", "collection", "position", "rotation", "scale", "scale3"]
	__optional__ = ["instance_properties"]
	__required_types__ = ["string", "string", "Point3", "Quat", "float", "Vector3"]
	__optional_types__ = ["InstancePropertyDesc"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"instance_properties": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.id = ""
		self.collection = ""
		self.position = Point3()
		self.rotation = Quat()
		self.scale = 1.0
		self.scale3 = Vector3()
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['CollectionInstanceDesc'] = CollectionInstanceDesc
		
		


class ComponenTypeDesc:
	__required__ = ["name_hash", "max_count"]
	__optional__ = []
	__required_types__ = ["uint64", "uint32"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.name_hash = 0
		self.max_count = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['ComponenTypeDesc'] = ComponenTypeDesc
		
		


class ComponentDesc:
	__required__ = ["id", "component", "position", "rotation", "property_decls", "scale"]
	__optional__ = ["properties"]
	__required_types__ = ["string", "string", "Point3", "Quat", "PropertyDeclarations", "Vector3"]
	__optional_types__ = ["PropertyDesc"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"properties": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.id = ""
		self.component = ""
		self.position = Point3()
		self.rotation = Quat()
		self.property_decls = PropertyDeclarations()
		self.scale = Vector3()
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['ComponentDesc'] = ComponentDesc
		
		


class ComponentPropertyDesc:
	__required__ = ["id", "property_decls"]
	__optional__ = ["properties"]
	__required_types__ = ["string", "PropertyDeclarations"]
	__optional_types__ = ["PropertyDesc"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"properties": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.id = ""
		self.property_decls = PropertyDeclarations()
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['ComponentPropertyDesc'] = ComponentPropertyDesc
		
		


class Disable:
	__required__ = []
	__optional__ = []
	__required_types__ = []
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['Disable'] = Disable
		
		


class EmbeddedComponentDesc:
	__required__ = ["id", "type", "data", "position", "rotation", "scale"]
	__optional__ = []
	__required_types__ = ["string", "string", "string", "Point3", "Quat", "Vector3"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.id = ""
		self.type = ""
		self.data = ""
		self.position = Point3()
		self.rotation = Quat()
		self.scale = Vector3()
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['EmbeddedComponentDesc'] = EmbeddedComponentDesc
		
		


class EmbeddedInstanceDesc:
	__required__ = ["id", "data", "position", "rotation", "scale", "scale3"]
	__optional__ = ["children", "component_properties"]
	__required_types__ = ["string", "string", "Point3", "Quat", "float", "Vector3"]
	__optional_types__ = ["string", "ComponentPropertyDesc"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"children": [], "component_properties": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.id = ""
		self.data = ""
		self.position = Point3()
		self.rotation = Quat()
		self.scale = 1.0
		self.scale3 = Vector3()
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['EmbeddedInstanceDesc'] = EmbeddedInstanceDesc
		
		


class Enable:
	__required__ = []
	__optional__ = []
	__required_types__ = []
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['Enable'] = Enable
		
		


class InstanceDesc:
	__required__ = ["id", "prototype", "position", "rotation", "scale", "scale3"]
	__optional__ = ["children", "component_properties"]
	__required_types__ = ["string", "string", "Point3", "Quat", "float", "Vector3"]
	__optional_types__ = ["string", "ComponentPropertyDesc"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"children": [], "component_properties": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.id = ""
		self.prototype = ""
		self.position = Point3()
		self.rotation = Quat()
		self.scale = 1.0
		self.scale3 = Vector3()
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['InstanceDesc'] = InstanceDesc
		
		


class InstancePropertyDesc:
	__required__ = ["id"]
	__optional__ = ["properties"]
	__required_types__ = ["string"]
	__optional_types__ = ["ComponentPropertyDesc"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"properties": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.id = ""
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['InstancePropertyDesc'] = InstancePropertyDesc
		
		


class LuaModule:
	__required__ = ["source", "properties"]
	__optional__ = ["modules", "resources", "property_resources"]
	__required_types__ = ["LuaSource", "PropertyDeclarations"]
	__optional_types__ = ["string", "string", "string"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"modules": [], "resources": [], "property_resources": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.source = LuaSource()
		self.properties = PropertyDeclarations()
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['LuaModule'] = LuaModule
		
		


class PropertyDeclarationEntry:
	__required__ = ["key", "id", "index"]
	__optional__ = ["element_ids"]
	__required_types__ = ["string", "uint64", "uint32"]
	__optional_types__ = ["uint64"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"element_ids": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.key = ""
		self.id = 0
		self.index = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['PropertyDeclarationEntry'] = PropertyDeclarationEntry
		
		


class PropertyDeclarations:
	__required__ = []
	__optional__ = ["number_entries", "hash_entries", "url_entries", "vector3_entries", "vector4_entries", "quat_entries", "bool_entries", "float_values", "hash_values", "string_values"]
	__required_types__ = []
	__optional_types__ = ["PropertyDeclarationEntry", "PropertyDeclarationEntry", "PropertyDeclarationEntry", "PropertyDeclarationEntry", "PropertyDeclarationEntry", "PropertyDeclarationEntry", "PropertyDeclarationEntry", "float", "uint64", "string"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"number_entries": [], "hash_entries": [], "url_entries": [], "vector3_entries": [], "vector4_entries": [], "quat_entries": [], "bool_entries": [], "float_values": [], "hash_values": [], "string_values": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['PropertyDeclarations'] = PropertyDeclarations
		
		


class PropertyDesc:
	__required__ = ["id", "value", "type"]
	__optional__ = []
	__required_types__ = ["string", "string", "enum"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.id = ""
		self.value = ""
		self.type = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['PropertyDesc'] = PropertyDesc
		
		


class PrototypeDesc:
	__required__ = []
	__optional__ = ["components", "embedded_components", "property_resources"]
	__required_types__ = []
	__optional_types__ = ["ComponentDesc", "EmbeddedComponentDesc", "string"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"components": [], "embedded_components": [], "property_resources": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['PrototypeDesc'] = PrototypeDesc
		
		


class ReleaseInputFocus:
	__required__ = []
	__optional__ = []
	__required_types__ = []
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['ReleaseInputFocus'] = ReleaseInputFocus
		
		


class ScriptMessage:
	__required__ = ["descriptor_hash", "payload_size", "function", "unref_function"]
	__optional__ = []
	__required_types__ = ["uint64", "uint32", "uint32", "bool"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.descriptor_hash = 0
		self.payload_size = 0
		self.function = 0
		self.unref_function = False
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['ScriptMessage'] = ScriptMessage
		
		


class SetParent:
	__required__ = ["parent_id", "keep_world_transform"]
	__optional__ = []
	__required_types__ = ["uint64", "uint32"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.parent_id = 0
		self.keep_world_transform = 1
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['SetParent'] = SetParent
		
		


class AcquireCameraFocus:
	__required__ = []
	__optional__ = []
	__required_types__ = []
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['AcquireCameraFocus'] = AcquireCameraFocus
		
		


class Animation:
	__required__ = ["id", "start_tile", "end_tile", "playback", "fps", "flip_horizontal", "flip_vertical"]
	__optional__ = ["cues"]
	__required_types__ = ["string", "uint32", "uint32", "enum", "uint32", "uint32", "uint32"]
	__optional_types__ = ["Cue"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"cues": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.id = ""
		self.start_tile = 0
		self.end_tile = 0
		self.playback = 1
		self.fps = 30
		self.flip_horizontal = 0
		self.flip_vertical = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['Animation'] = Animation
		
		


class AnimationDone:
	__required__ = ["current_tile", "id"]
	__optional__ = []
	__required_types__ = ["uint32", "uint64"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.current_tile = 0
		self.id = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['AnimationDone'] = AnimationDone
		
		


class ApplyForce:
	__required__ = ["force", "position"]
	__optional__ = []
	__required_types__ = ["Vector3", "Point3"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.force = Vector3()
		self.position = Point3()
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['ApplyForce'] = ApplyForce
		
		


class Atlas:
	__required__ = ["margin", "extrude_borders", "inner_padding", "max_page_width", "max_page_height", "rename_patterns"]
	__optional__ = ["images", "animations"]
	__required_types__ = ["uint32", "uint32", "uint32", "uint32", "uint32", "string"]
	__optional_types__ = ["AtlasImage", "AtlasAnimation"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"images": [], "animations": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.margin = 0
		self.extrude_borders = 0
		self.inner_padding = 0
		self.max_page_width = 0
		self.max_page_height = 0
		self.rename_patterns = ""
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['Atlas'] = Atlas
		
		


class AtlasAnimation:
	__required__ = ["id", "playback", "fps", "flip_horizontal", "flip_vertical"]
	__optional__ = ["images"]
	__required_types__ = ["string", "enum", "uint32", "uint32", "uint32"]
	__optional_types__ = ["AtlasImage"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"images": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.id = ""
		self.playback = 1
		self.fps = 30
		self.flip_horizontal = 0
		self.flip_vertical = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['AtlasAnimation'] = AtlasAnimation
		
		


class AtlasImage:
	__required__ = ["image", "sprite_trim_mode"]
	__optional__ = []
	__required_types__ = ["string", "enum"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.image = ""
		self.sprite_trim_mode = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['AtlasImage'] = AtlasImage
		
		


class BufferDesc:
	__required__ = []
	__optional__ = ["streams"]
	__required_types__ = []
	__optional_types__ = ["StreamDesc"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"streams": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['BufferDesc'] = BufferDesc
		
		


class CameraDesc:
	__required__ = ["aspect_ratio", "fov", "near_z", "far_z", "auto_aspect_ratio", "orthographic_projection", "orthographic_zoom"]
	__optional__ = []
	__required_types__ = ["float", "float", "float", "float", "uint32", "uint32", "float"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.aspect_ratio = 0.0
		self.fov = 0.0
		self.near_z = 0.0
		self.far_z = 0.0
		self.auto_aspect_ratio = 0
		self.orthographic_projection = 0
		self.orthographic_zoom = 1.0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['CameraDesc'] = CameraDesc
		
		


class CollectionFactoryDesc:
	__required__ = ["prototype", "load_dynamically", "dynamic_prototype"]
	__optional__ = []
	__required_types__ = ["string", "bool", "bool"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.prototype = ""
		self.load_dynamically = False
		self.dynamic_prototype = False
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['CollectionFactoryDesc'] = CollectionFactoryDesc
		
		


class CollectionProxyDesc:
	__required__ = ["collection", "exclude"]
	__optional__ = []
	__required_types__ = ["string", "bool"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.collection = ""
		self.exclude = False
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['CollectionProxyDesc'] = CollectionProxyDesc
		
		


class Collision:
	__required__ = ["position", "id", "group"]
	__optional__ = []
	__required_types__ = ["Point3", "uint64", "uint64"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.position = Point3()
		self.id = 0
		self.group = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['Collision'] = Collision
		
		


class CollisionEvent:
	__required__ = ["a", "b"]
	__optional__ = []
	__required_types__ = ["Collision", "Collision"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.a = Collision()
		self.b = Collision()
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['CollisionEvent'] = CollisionEvent
		
		


class CollisionObjectDesc:
	__required__ = ["collision_shape", "type", "mass", "friction", "restitution", "group", "embedded_collision_shape", "linear_damping", "angular_damping", "locked_rotation", "bullet"]
	__optional__ = ["mask"]
	__required_types__ = ["string", "enum", "float", "float", "float", "string", "CollisionShape", "float", "float", "bool", "bool"]
	__optional_types__ = ["string"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"mask": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.collision_shape = ""
		self.type = 0
		self.mass = 0.0
		self.friction = 0.0
		self.restitution = 0.0
		self.group = ""
		self.embedded_collision_shape = CollisionShape()
		self.linear_damping = 0.0
		self.angular_damping = 0.0
		self.locked_rotation = False
		self.bullet = False
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['CollisionObjectDesc'] = CollisionObjectDesc
		
		


class CollisionResponse:
	__required__ = ["other_id", "group", "other_position", "other_group", "own_group"]
	__optional__ = []
	__required_types__ = ["uint64", "uint64", "Point3", "uint64", "uint64"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.other_id = 0
		self.group = 0
		self.other_position = Point3()
		self.other_group = 0
		self.own_group = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['CollisionResponse'] = CollisionResponse
		
		


class CollisionShape:
	__required__ = []
	__optional__ = ["shapes", "data"]
	__required_types__ = []
	__optional_types__ = ["Shape", "float"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"shapes": [], "data": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['CollisionShape'] = CollisionShape
		
		


class ContactPoint:
	__required__ = ["position", "normal", "relative_velocity", "mass", "id", "group"]
	__optional__ = []
	__required_types__ = ["Point3", "Vector3", "Vector3", "float", "uint64", "uint64"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.position = Point3()
		self.normal = Vector3()
		self.relative_velocity = Vector3()
		self.mass = 0.0
		self.id = 0
		self.group = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['ContactPoint'] = ContactPoint
		
		


class ContactPointEvent:
	__required__ = ["a", "b", "distance", "applied_impulse"]
	__optional__ = []
	__required_types__ = ["ContactPoint", "ContactPoint", "float", "float"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.a = ContactPoint()
		self.b = ContactPoint()
		self.distance = 0.0
		self.applied_impulse = 0.0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['ContactPointEvent'] = ContactPointEvent
		
		


class ContactPointResponse:
	__required__ = ["position", "normal", "relative_velocity", "distance", "applied_impulse", "life_time", "mass", "other_mass", "other_id", "other_position", "group", "other_group", "own_group"]
	__optional__ = []
	__required_types__ = ["Point3", "Vector3", "Vector3", "float", "float", "float", "float", "float", "uint64", "Point3", "uint64", "uint64", "uint64"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.position = Point3()
		self.normal = Vector3()
		self.relative_velocity = Vector3()
		self.distance = 0.0
		self.applied_impulse = 0.0
		self.life_time = 0.0
		self.mass = 0.0
		self.other_mass = 0.0
		self.other_id = 0
		self.other_position = Point3()
		self.group = 0
		self.other_group = 0
		self.own_group = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['ContactPointResponse'] = ContactPointResponse
		
		


class ConvexHull:
	__required__ = ["index", "count", "collision_group"]
	__optional__ = []
	__required_types__ = ["uint32", "uint32", "string"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.index = 0
		self.count = 0
		self.collision_group = "tile"
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['ConvexHull'] = ConvexHull
		
		


class ConvexShape:
	__required__ = ["shape_type"]
	__optional__ = ["data"]
	__required_types__ = ["enum"]
	__optional_types__ = ["float"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"data": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.shape_type = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['ConvexShape'] = ConvexShape
		
		


class Create:
	__required__ = ["position", "rotation", "id", "scale", "scale3", "index"]
	__optional__ = []
	__required_types__ = ["Point3", "Quat", "uint64", "float", "Vector3", "uint32"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.position = Point3()
		self.rotation = Quat()
		self.id = 0
		self.scale = 1.0
		self.scale3 = Vector3()
		self.index = 4294967295
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['Create'] = Create
		
		


class Cue:
	__required__ = ["id", "frame", "value"]
	__optional__ = []
	__required_types__ = ["string", "uint32", "float"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.id = ""
		self.frame = 0
		self.value = 0.0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['Cue'] = Cue
		
		


class EnableGridShapeLayer:
	__required__ = ["shape", "enable"]
	__optional__ = []
	__required_types__ = ["uint32", "uint32"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.shape = 0
		self.enable = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['EnableGridShapeLayer'] = EnableGridShapeLayer
		
		


class FactoryDesc:
	__required__ = ["prototype", "load_dynamically", "dynamic_prototype"]
	__optional__ = []
	__required_types__ = ["string", "bool", "bool"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.prototype = ""
		self.load_dynamically = False
		self.dynamic_prototype = False
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['FactoryDesc'] = FactoryDesc
		
		


class LabelDesc:
	__required__ = ["size", "scale", "color", "outline", "shadow", "leading", "tracking", "pivot", "blend_mode", "line_break", "text", "font", "material"]
	__optional__ = []
	__required_types__ = ["Vector4", "Vector4", "Vector4", "Vector4", "Vector4", "float", "float", "enum", "enum", "bool", "string", "string", "string"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.size = Vector4()
		self.scale = Vector4()
		self.color = Vector4()
		self.outline = Vector4()
		self.shadow = Vector4()
		self.leading = 0.0
		self.tracking = 0.0
		self.pivot = 0
		self.blend_mode = 0
		self.line_break = False
		self.text = ""
		self.font = ""
		self.material = ""
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['LabelDesc'] = LabelDesc
		
		


class LayoutChanged:
	__required__ = ["id", "previous_id"]
	__optional__ = []
	__required_types__ = ["uint64", "uint64"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.id = 0
		self.previous_id = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['LayoutChanged'] = LayoutChanged
		
		


class LightDesc:
	__required__ = ["id", "type", "intensity", "color", "range", "decay", "cone_angle", "penumbra_angle", "drop_off"]
	__optional__ = []
	__required_types__ = ["string", "enum", "float", "Vector3", "float", "float", "float", "float", "float"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.id = ""
		self.type = 0
		self.intensity = 0.0
		self.color = Vector3()
		self.range = 0.0
		self.decay = 0.0
		self.cone_angle = 0.0
		self.penumbra_angle = 0.0
		self.drop_off = 0.0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['LightDesc'] = LightDesc
		
		


class Material:
	__required__ = ["name", "material"]
	__optional__ = ["textures", "attributes"]
	__required_types__ = ["string", "string"]
	__optional_types__ = ["Texture", "VertexAttribute"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"textures": [], "attributes": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.name = ""
		self.material = ""
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['Material'] = Material
		
		


class MeshDesc:
	__required__ = ["material", "vertices", "primitive_type", "position_stream", "normal_stream"]
	__optional__ = ["textures"]
	__required_types__ = ["string", "string", "enum", "string", "string"]
	__optional_types__ = ["string"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"textures": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.material = ""
		self.vertices = ""
		self.primitive_type = 4
		self.position_stream = ""
		self.normal_stream = ""
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['MeshDesc'] = MeshDesc
		
		


class Model:
	__required__ = ["local", "id", "bone_id"]
	__optional__ = ["meshes"]
	__required_types__ = ["Transform", "uint64", "uint64"]
	__optional_types__ = ["Mesh"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"meshes": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.local = Transform()
		self.id = 0
		self.bone_id = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['Model'] = Model
		
		


class ModelAnimationDone:
	__required__ = ["animation_id", "playback"]
	__optional__ = []
	__required_types__ = ["uint64", "uint32"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.animation_id = 0
		self.playback = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['ModelAnimationDone'] = ModelAnimationDone
		
		


class ModelCancelAnimation:
	__required__ = []
	__optional__ = []
	__required_types__ = []
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['ModelCancelAnimation'] = ModelCancelAnimation
		
		


class ModelDesc:
	__required__ = ["mesh", "material", "skeleton", "animations", "default_animation", "name"]
	__optional__ = ["textures", "materials"]
	__required_types__ = ["string", "string", "string", "string", "string", "string"]
	__optional_types__ = ["string", "Material"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"textures": [], "materials": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.mesh = ""
		self.material = ""
		self.skeleton = ""
		self.animations = ""
		self.default_animation = ""
		self.name = ""
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['ModelDesc'] = ModelDesc
		
		


class ModelPlayAnimation:
	__required__ = ["animation_id", "playback", "blend_duration", "offset", "playback_rate"]
	__optional__ = []
	__required_types__ = ["uint64", "uint32", "float", "float", "float"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.animation_id = 0
		self.playback = 0
		self.blend_duration = 0.0
		self.offset = 0.0
		self.playback_rate = 1.0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['ModelPlayAnimation'] = ModelPlayAnimation
		
		


class NodeDesc:
	__required__ = ["position", "rotation", "scale", "size", "color", "type", "blend_mode", "text", "texture", "font", "id", "xanchor", "yanchor", "pivot", "outline", "shadow", "adjust_mode", "line_break", "parent", "layer", "inherit_alpha", "slice9", "outerBounds", "innerRadius", "perimeterVertices", "pieFillAngle", "clipping_mode", "clipping_visible", "clipping_inverted", "alpha", "outline_alpha", "shadow_alpha", "template", "template_node_child", "text_leading", "text_tracking", "size_mode", "spine_scene", "spine_default_animation", "spine_skin", "spine_node_child", "particlefx", "custom_type", "enabled", "visible", "material"]
	__optional__ = ["overridden_fields"]
	__required_types__ = ["Vector4", "Vector4", "Vector4", "Vector4", "Vector4", "enum", "enum", "string", "string", "string", "string", "enum", "enum", "enum", "Vector4", "Vector4", "enum", "bool", "string", "string", "bool", "Vector4", "enum", "float", "int32", "float", "enum", "bool", "bool", "float", "float", "float", "string", "bool", "float", "float", "enum", "string", "string", "string", "bool", "string", "uint32", "bool", "bool", "string"]
	__optional_types__ = ["uint32"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"overridden_fields": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.position = Vector4()
		self.rotation = Vector4()
		self.scale = Vector4()
		self.size = Vector4()
		self.color = Vector4()
		self.type = 0
		self.blend_mode = 0
		self.text = ""
		self.texture = ""
		self.font = ""
		self.id = ""
		self.xanchor = 0
		self.yanchor = 0
		self.pivot = 0
		self.outline = Vector4()
		self.shadow = Vector4()
		self.adjust_mode = 0
		self.line_break = False
		self.parent = ""
		self.layer = ""
		self.inherit_alpha = False
		self.slice9 = Vector4()
		self.outerBounds = 1
		self.innerRadius = 0.0
		self.perimeterVertices = 32
		self.pieFillAngle = 360.0
		self.clipping_mode = 0
		self.clipping_visible = True
		self.clipping_inverted = False
		self.alpha = 1.0
		self.outline_alpha = 1.0
		self.shadow_alpha = 1.0
		self.template = ""
		self.template_node_child = False
		self.text_leading = 1.0
		self.text_tracking = 0.0
		self.size_mode = 0
		self.spine_scene = ""
		self.spine_default_animation = ""
		self.spine_skin = ""
		self.spine_node_child = False
		self.particlefx = ""
		self.custom_type = 0
		self.enabled = True
		self.visible = True
		self.material = ""
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['NodeDesc'] = NodeDesc
		
		


class PauseSound:
	__required__ = ["pause"]
	__optional__ = []
	__required_types__ = ["bool"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.pause = True
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['PauseSound'] = PauseSound
		
		


class PlayAnimation:
	__required__ = ["id", "offset", "playback_rate"]
	__optional__ = []
	__required_types__ = ["uint64", "float", "float"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.id = 0
		self.offset = 0.0
		self.playback_rate = 1.0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['PlayAnimation'] = PlayAnimation
		
		


class PlayParticleFX:
	__required__ = []
	__optional__ = []
	__required_types__ = []
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['PlayParticleFX'] = PlayParticleFX
		
		


class PlaySound:
	__required__ = ["delay", "gain", "pan", "speed", "play_id"]
	__optional__ = []
	__required_types__ = ["float", "float", "float", "float", "uint32"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.delay = 0.0
		self.gain = 1.0
		self.pan = 0.0
		self.speed = 1.0
		self.play_id = 4294967295
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['PlaySound'] = PlaySound
		
		


class RayCastMissed:
	__required__ = ["request_id"]
	__optional__ = []
	__required_types__ = ["uint32"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.request_id = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['RayCastMissed'] = RayCastMissed
		
		


class RayCastResponse:
	__required__ = ["fraction", "position", "normal", "id", "group", "request_id"]
	__optional__ = []
	__required_types__ = ["float", "Point3", "Vector3", "uint64", "uint64", "uint32"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.fraction = 0.0
		self.position = Point3()
		self.normal = Vector3()
		self.id = 0
		self.group = 0
		self.request_id = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['RayCastResponse'] = RayCastResponse
		
		


class ReleaseCameraFocus:
	__required__ = []
	__optional__ = []
	__required_types__ = []
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['ReleaseCameraFocus'] = ReleaseCameraFocus
		
		


class RequestRayCast:
	__required__ = []
	__optional__ = []
	__required_types__ = ["Point3", "Point3", "uint32", "uint32"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['RequestRayCast'] = RequestRayCast
		
		


class RequestVelocity:
	__required__ = []
	__optional__ = []
	__required_types__ = []
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['RequestVelocity'] = RequestVelocity
		
		


class ResetConstant:
	__required__ = ["name_hash"]
	__optional__ = []
	__required_types__ = ["uint64"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.name_hash = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['ResetConstant'] = ResetConstant
		
		


class ResetConstantParticleFX:
	__required__ = ["emitter_id", "name_hash"]
	__optional__ = []
	__required_types__ = ["uint64", "uint64"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.emitter_id = 0
		self.name_hash = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['ResetConstantParticleFX'] = ResetConstantParticleFX
		
		


class ResetConstantTileMap:
	__required__ = ["name_hash"]
	__optional__ = []
	__required_types__ = ["uint64"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.name_hash = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['ResetConstantTileMap'] = ResetConstantTileMap
		
		


class SceneDesc:
	__required__ = ["script", "background_color", "material", "adjust_reference", "max_nodes"]
	__optional__ = ["fonts", "textures", "nodes", "layers", "layouts", "spine_scenes", "particlefxs", "resources", "materials"]
	__required_types__ = ["string", "Vector4", "string", "enum", "uint32"]
	__optional_types__ = ["FontDesc", "TextureDesc", "NodeDesc", "LayerDesc", "LayoutDesc", "SpineSceneDesc", "ParticleFXDesc", "ResourceDesc", "MaterialDesc"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"fonts": [], "textures": [], "nodes": [], "layers": [], "layouts": [], "spine_scenes": [], "particlefxs": [], "resources": [], "materials": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.script = ""
		self.background_color = Vector4()
		self.material = "/builtins/materials/gui.material"
		self.adjust_reference = 0
		self.max_nodes = 512
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['SceneDesc'] = SceneDesc
		
		


class SetCamera:
	__required__ = ["aspect_ratio", "fov", "near_z", "far_z", "orthographic_projection", "orthographic_zoom"]
	__optional__ = []
	__required_types__ = ["float", "float", "float", "float", "uint32", "float"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.aspect_ratio = 0.0
		self.fov = 0.0
		self.near_z = 0.0
		self.far_z = 0.0
		self.orthographic_projection = 0
		self.orthographic_zoom = 1.0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['SetCamera'] = SetCamera
		
		


class SetConstant:
	__required__ = ["name_hash", "value", "index"]
	__optional__ = []
	__required_types__ = ["uint64", "Vector4", "int32"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.name_hash = 0
		self.value = Vector4()
		self.index = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['SetConstant'] = SetConstant
		
		


class SetConstantParticleFX:
	__required__ = ["emitter_id", "name_hash", "value", "is_matrix4"]
	__optional__ = []
	__required_types__ = ["uint64", "uint64", "Matrix4", "bool"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.emitter_id = 0
		self.name_hash = 0
		self.value = Matrix4()
		self.is_matrix4 = False
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['SetConstantParticleFX'] = SetConstantParticleFX
		
		


class SetConstantTileMap:
	__required__ = ["name_hash", "value"]
	__optional__ = []
	__required_types__ = ["uint64", "Vector4"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.name_hash = 0
		self.value = Vector4()
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['SetConstantTileMap'] = SetConstantTileMap
		
		


class SetFlipHorizontal:
	__required__ = ["flip"]
	__optional__ = []
	__required_types__ = ["uint32"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.flip = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['SetFlipHorizontal'] = SetFlipHorizontal
		
		


class SetFlipVertical:
	__required__ = ["flip"]
	__optional__ = []
	__required_types__ = ["uint32"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.flip = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['SetFlipVertical'] = SetFlipVertical
		
		


class SetGain:
	__required__ = ["gain"]
	__optional__ = []
	__required_types__ = ["float"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.gain = 1.0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['SetGain'] = SetGain
		
		


class SetGridShapeHull:
	__required__ = ["shape", "row", "column", "hull", "flip_horizontal", "flip_vertical", "rotate90"]
	__optional__ = []
	__required_types__ = ["uint32", "uint32", "uint32", "uint32", "uint32", "uint32", "uint32"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.shape = 0
		self.row = 0
		self.column = 0
		self.hull = 0
		self.flip_horizontal = 0
		self.flip_vertical = 0
		self.rotate90 = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['SetGridShapeHull'] = SetGridShapeHull
		
		


class SetLight:
	__required__ = ["position", "rotation", "light"]
	__optional__ = []
	__required_types__ = ["Point3", "Quat", "LightDesc"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.position = Point3()
		self.rotation = Quat()
		self.light = LightDesc()
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['SetLight'] = SetLight
		
		


class SetPan:
	__required__ = ["pan"]
	__optional__ = []
	__required_types__ = ["float"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.pan = 0.0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['SetPan'] = SetPan
		
		


class SetScale:
	__required__ = ["scale"]
	__optional__ = []
	__required_types__ = ["Vector3"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.scale = Vector3()
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['SetScale'] = SetScale
		
		


class SetSpeed:
	__required__ = ["speed"]
	__optional__ = []
	__required_types__ = ["float"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.speed = 1.0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['SetSpeed'] = SetSpeed
		
		


class SetText:
	__required__ = ["text"]
	__optional__ = []
	__required_types__ = ["string"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.text = ""
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['SetText'] = SetText
		
		


class SetTexture:
	__required__ = ["texture_hash", "texture_unit"]
	__optional__ = []
	__required_types__ = ["uint64", "uint32"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.texture_hash = 0
		self.texture_unit = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['SetTexture'] = SetTexture
		
		


class SetTimeStep:
	__required__ = ["factor", "mode"]
	__optional__ = []
	__required_types__ = ["float", "enum"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.factor = 0.0
		self.mode = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['SetTimeStep'] = SetTimeStep
		
		


class SetViewProjection:
	__required__ = ["id", "view", "projection"]
	__optional__ = []
	__required_types__ = ["uint64", "Matrix4", "Matrix4"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.id = 0
		self.view = Matrix4()
		self.projection = Matrix4()
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['SetViewProjection'] = SetViewProjection
		
		


class SoundDesc:
	__required__ = ["sound", "looping", "group", "gain", "pan", "speed", "loopcount"]
	__optional__ = []
	__required_types__ = ["string", "int32", "string", "float", "float", "float", "int32"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.sound = ""
		self.looping = 0
		self.group = "master"
		self.gain = 1.0
		self.pan = 0.0
		self.speed = 1.0
		self.loopcount = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['SoundDesc'] = SoundDesc
		
		


class SoundEvent:
	__required__ = ["play_id"]
	__optional__ = []
	__required_types__ = ["int32"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.play_id = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['SoundEvent'] = SoundEvent
		
		


class SpriteDesc:
	__required__ = ["tile_set", "default_animation", "material", "blend_mode", "slice9", "size", "size_mode", "offset", "playback_rate"]
	__optional__ = ["attributes", "textures"]
	__required_types__ = ["string", "string", "string", "enum", "Vector4", "Vector4", "enum", "float", "float"]
	__optional_types__ = ["VertexAttribute", "SpriteTexture"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"attributes": [], "textures": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.tile_set = ""
		self.default_animation = ""
		self.material = "/builtins/materials/sprite.material"
		self.blend_mode = 0
		self.slice9 = Vector4()
		self.size = Vector4()
		self.size_mode = 1
		self.offset = 0.0
		self.playback_rate = 1.0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['SpriteDesc'] = SpriteDesc
		
		


class SpriteGeometry:
	__required__ = ["width", "height", "center_x", "center_y", "rotated", "trim_mode"]
	__optional__ = ["vertices", "uvs", "indices"]
	__required_types__ = ["uint32", "uint32", "float", "float", "bool", "enum"]
	__optional_types__ = ["float", "float", "uint32"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"vertices": [], "uvs": [], "indices": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.width = 0
		self.height = 0
		self.center_x = 0.0
		self.center_y = 0.0
		self.rotated = False
		self.trim_mode = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['SpriteGeometry'] = SpriteGeometry
		
		


class SpriteTexture:
	__required__ = ["sampler", "texture"]
	__optional__ = []
	__required_types__ = ["string", "string"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.sampler = ""
		self.texture = ""
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['SpriteTexture'] = SpriteTexture
		
		


class StopParticleFX:
	__required__ = ["clear_particles"]
	__optional__ = []
	__required_types__ = ["bool"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.clear_particles = False
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['StopParticleFX'] = StopParticleFX
		
		


class StopSound:
	__required__ = ["play_id"]
	__optional__ = []
	__required_types__ = ["uint32"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.play_id = 4294967295
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['StopSound'] = StopSound
		
		


class StreamDesc:
	__required__ = ["name", "value_type", "value_count", "name_hash"]
	__optional__ = ["ui", "i", "ui64", "i64", "f"]
	__required_types__ = ["string", "enum", "uint32", "uint64"]
	__optional_types__ = ["uint32", "int32", "uint64", "int64", "float"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"ui": [], "i": [], "ui64": [], "i64": [], "f": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.name = ""
		self.value_type = 0
		self.value_count = 0
		self.name_hash = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['StreamDesc'] = StreamDesc
		
		


class Texture:
	__required__ = ["sampler", "texture"]
	__optional__ = []
	__required_types__ = ["string", "string"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.sampler = ""
		self.texture = ""
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['Texture'] = Texture
		
		


class TextureSet:
	__required__ = ["texture", "width", "height", "texture_hash", "tile_width", "tile_height", "tile_count", "tex_coords", "tex_dims", "use_geometries", "page_count"]
	__optional__ = ["animations", "collision_hull_points", "collision_groups", "convex_hulls", "image_name_hashes", "frame_indices", "geometries", "page_indices"]
	__required_types__ = ["string", "uint32", "uint32", "uint64", "uint32", "uint32", "uint32", "bytes", "bytes", "uint32", "uint32"]
	__optional_types__ = ["TextureSetAnimation", "float", "string", "ConvexHull", "uint64", "uint32", "SpriteGeometry", "uint32"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"animations": [], "collision_hull_points": [], "collision_groups": [], "convex_hulls": [], "image_name_hashes": [], "frame_indices": [], "geometries": [], "page_indices": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.texture = ""
		self.width = 0
		self.height = 0
		self.texture_hash = 0
		self.tile_width = 0
		self.tile_height = 0
		self.tile_count = 0
		self.tex_coords = ""
		self.tex_dims = ""
		self.use_geometries = 0
		self.page_count = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['TextureSet'] = TextureSet
		
		


class TextureSetAnimation:
	__required__ = ["id", "width", "height", "start", "end", "fps", "playback", "flip_horizontal", "flip_vertical"]
	__optional__ = []
	__required_types__ = ["string", "uint32", "uint32", "uint32", "uint32", "uint32", "enum", "uint32", "uint32"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.id = ""
		self.width = 0
		self.height = 0
		self.start = 0
		self.end = 0
		self.fps = 30
		self.playback = 1
		self.flip_horizontal = 0
		self.flip_vertical = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['TextureSetAnimation'] = TextureSetAnimation
		
		


class TileCell:
	__required__ = ["x", "y", "tile", "h_flip", "v_flip", "rotate90"]
	__optional__ = []
	__required_types__ = ["int32", "int32", "uint32", "uint32", "uint32", "uint32"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.x = 0
		self.y = 0
		self.tile = 0
		self.h_flip = 0
		self.v_flip = 0
		self.rotate90 = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['TileCell'] = TileCell
		
		


class TileGrid:
	__required__ = ["tile_set", "material", "blend_mode"]
	__optional__ = ["layers"]
	__required_types__ = ["string", "string", "enum"]
	__optional_types__ = ["TileLayer"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"layers": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.tile_set = ""
		self.material = "/builtins/materials/tile_map.material"
		self.blend_mode = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['TileGrid'] = TileGrid
		
		


class TileLayer:
	__required__ = ["id", "z", "is_visible", "id_hash"]
	__optional__ = ["cell"]
	__required_types__ = ["string", "float", "uint32", "uint64"]
	__optional_types__ = ["TileCell"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"cell": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.id = "layer1"
		self.z = 0.0
		self.is_visible = 1
		self.id_hash = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['TileLayer'] = TileLayer
		
		


class TileSet:
	__required__ = ["image", "tile_width", "tile_height", "tile_margin", "tile_spacing", "collision", "material_tag", "extrude_borders", "inner_padding", "sprite_trim_mode"]
	__optional__ = ["convex_hulls", "convex_hull_points", "collision_groups", "animations"]
	__required_types__ = ["string", "uint32", "uint32", "uint32", "uint32", "string", "string", "uint32", "uint32", "enum"]
	__optional_types__ = ["ConvexHull", "float", "string", "Animation"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"convex_hulls": [], "convex_hull_points": [], "collision_groups": [], "animations": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.image = ""
		self.tile_width = 0
		self.tile_height = 0
		self.tile_margin = 0
		self.tile_spacing = 0
		self.collision = ""
		self.material_tag = "tile"
		self.extrude_borders = 0
		self.inner_padding = 0
		self.sprite_trim_mode = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['TileSet'] = TileSet
		
		


class Trigger:
	__required__ = ["id", "group"]
	__optional__ = []
	__required_types__ = ["uint64", "uint64"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.id = 0
		self.group = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['Trigger'] = Trigger
		
		


class TriggerEvent:
	__required__ = ["enter", "a", "b"]
	__optional__ = []
	__required_types__ = ["bool", "Trigger", "Trigger"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.enter = False
		self.a = Trigger()
		self.b = Trigger()
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['TriggerEvent'] = TriggerEvent
		
		


class TriggerResponse:
	__required__ = ["other_id", "enter", "group", "other_group", "own_group"]
	__optional__ = []
	__required_types__ = ["uint64", "bool", "uint64", "uint64", "uint64"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.other_id = 0
		self.enter = False
		self.group = 0
		self.other_group = 0
		self.own_group = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['TriggerResponse'] = TriggerResponse
		
		


class VelocityResponse:
	__required__ = ["linear_velocity", "angular_velocity"]
	__optional__ = []
	__required_types__ = ["Vector3", "Vector3"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.linear_velocity = Vector3()
		self.angular_velocity = Vector3()
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['VelocityResponse'] = VelocityResponse
		
		


class Cubemap:
	__required__ = ["right", "left", "top", "bottom", "front", "back"]
	__optional__ = []
	__required_types__ = ["string", "string", "string", "string", "string", "string"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.right = ""
		self.left = ""
		self.top = ""
		self.bottom = ""
		self.front = ""
		self.back = ""
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['Cubemap'] = Cubemap
		
		


class PathSettings:
	__required__ = ["path", "profile"]
	__optional__ = []
	__required_types__ = ["string", "string"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.path = ""
		self.profile = ""
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['PathSettings'] = PathSettings
		
		


class PlatformProfile:
	__required__ = ["os", "mipmaps", "max_texture_size", "premultiply_alpha"]
	__optional__ = ["formats"]
	__required_types__ = ["enum", "bool", "uint32", "bool"]
	__optional_types__ = ["TextureFormatAlternative"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"formats": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.os = 0
		self.mipmaps = False
		self.max_texture_size = 0
		self.premultiply_alpha = True
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['PlatformProfile'] = PlatformProfile
		
		


class ShaderDesc:
	__required__ = ["shader_class"]
	__optional__ = ["shaders"]
	__required_types__ = ["enum"]
	__optional_types__ = ["Shader"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"shaders": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.shader_class = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['ShaderDesc'] = ShaderDesc
		
		


class TextureFormatAlternative:
	__required__ = ["format", "compression_level", "compression_type"]
	__optional__ = []
	__required_types__ = ["enum", "enum", "enum"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.format = 0
		self.compression_level = 0
		self.compression_type = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['TextureFormatAlternative'] = TextureFormatAlternative
		
		


class TextureImage:
	__required__ = ["type", "count", "usage_flags"]
	__optional__ = ["alternatives"]
	__required_types__ = ["enum", "uint32", "uint32"]
	__optional_types__ = ["Image"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"alternatives": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.type = 1
		self.count = 0
		self.usage_flags = 1
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['TextureImage'] = TextureImage
		
		


class TextureProfile:
	__required__ = ["name"]
	__optional__ = ["platforms"]
	__required_types__ = ["string"]
	__optional_types__ = ["PlatformProfile"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"platforms": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.name = ""
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['TextureProfile'] = TextureProfile
		
		


class TextureProfiles:
	__required__ = []
	__optional__ = ["path_settings", "profiles"]
	__required_types__ = []
	__optional_types__ = ["PathSettings", "TextureProfile"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"path_settings": [], "profiles": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['TextureProfiles'] = TextureProfiles
		
		


class VertexAttribute:
	__required__ = ["name", "name_hash", "semantic_type", "element_count", "normalize", "data_type", "coordinate_space", "long_values", "double_values", "binary_values"]
	__optional__ = []
	__required_types__ = ["string", "uint64", "enum", "int32", "bool", "enum", "enum", "LongValues", "DoubleValues", "bytes"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.name = ""
		self.name_hash = 0
		self.semantic_type = 1
		self.element_count = 0
		self.normalize = False
		self.data_type = 7
		self.coordinate_space = 2
		self.binary_values = ""
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['VertexAttribute'] = VertexAttribute
		
		


class GamepadMap:
	__required__ = ["device", "platform", "dead_zone"]
	__optional__ = ["map"]
	__required_types__ = ["string", "string", "float"]
	__optional_types__ = ["GamepadMapEntry"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"map": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.device = ""
		self.platform = ""
		self.dead_zone = 0.0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['GamepadMap'] = GamepadMap
		
		


class GamepadMapEntry:
	__required__ = ["input", "type", "index", "hat_mask"]
	__optional__ = ["mod"]
	__required_types__ = ["enum", "enum", "uint32", "uint32"]
	__optional_types__ = ["GamepadModifier_t"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"mod": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.input = 0
		self.type = 0
		self.index = 0
		self.hat_mask = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['GamepadMapEntry'] = GamepadMapEntry
		
		


class GamepadMaps:
	__required__ = []
	__optional__ = ["driver"]
	__required_types__ = []
	__optional_types__ = ["GamepadMap"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"driver": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['GamepadMaps'] = GamepadMaps
		
		


class GamepadModifier_t:
	__required__ = ["mod"]
	__optional__ = []
	__required_types__ = ["enum"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.mod = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['GamepadModifier_t'] = GamepadModifier_t
		
		


class GamepadTrigger:
	__required__ = ["input", "action"]
	__optional__ = []
	__required_types__ = ["enum", "string"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.input = 0
		self.action = ""
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['GamepadTrigger'] = GamepadTrigger
		
		


class InputBinding:
	__required__ = []
	__optional__ = ["key_trigger", "mouse_trigger", "gamepad_trigger", "touch_trigger", "text_trigger"]
	__required_types__ = []
	__optional_types__ = ["KeyTrigger", "MouseTrigger", "GamepadTrigger", "TouchTrigger", "TextTrigger"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"key_trigger": [], "mouse_trigger": [], "gamepad_trigger": [], "touch_trigger": [], "text_trigger": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['InputBinding'] = InputBinding
		
		


class KeyTrigger:
	__required__ = ["input", "action"]
	__optional__ = []
	__required_types__ = ["enum", "string"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.input = 0
		self.action = ""
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['KeyTrigger'] = KeyTrigger
		
		


class MouseTrigger:
	__required__ = ["input", "action"]
	__optional__ = []
	__required_types__ = ["enum", "string"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.input = 0
		self.action = ""
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['MouseTrigger'] = MouseTrigger
		
		


class TextTrigger:
	__required__ = ["input", "action"]
	__optional__ = []
	__required_types__ = ["enum", "string"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.input = 0
		self.action = ""
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['TextTrigger'] = TextTrigger
		
		


class TouchTrigger:
	__required__ = ["input", "action"]
	__optional__ = []
	__required_types__ = ["enum", "string"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.input = 0
		self.action = ""
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['TouchTrigger'] = TouchTrigger
		
		


class Emitter:
	__required__ = ["id", "mode", "duration", "space", "position", "rotation", "tile_source", "animation", "material", "blend_mode", "particle_orientation", "inherit_velocity", "max_particle_count", "type", "start_delay", "size_mode", "start_delay_spread", "duration_spread", "stretch_with_velocity", "start_offset", "pivot"]
	__optional__ = ["properties", "particle_properties", "modifiers", "attributes"]
	__required_types__ = ["string", "enum", "float", "enum", "Point3", "Quat", "string", "string", "string", "enum", "enum", "float", "uint32", "enum", "float", "enum", "float", "float", "bool", "float", "Point3"]
	__optional_types__ = ["Property", "ParticleProperty", "Modifier", "VertexAttribute"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"properties": [], "particle_properties": [], "modifiers": [], "attributes": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.id = "emitter"
		self.mode = 0
		self.duration = 0.0
		self.space = 0
		self.position = Point3()
		self.rotation = Quat()
		self.tile_source = ""
		self.animation = ""
		self.material = ""
		self.blend_mode = 0
		self.particle_orientation = 0
		self.inherit_velocity = 0.0
		self.max_particle_count = 0
		self.type = 0
		self.start_delay = 0.0
		self.size_mode = 0
		self.start_delay_spread = 0.0
		self.duration_spread = 0.0
		self.stretch_with_velocity = False
		self.start_offset = 0.0
		self.pivot = Point3()
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['Emitter'] = Emitter
		
		


class Modifier:
	__required__ = ["type", "use_direction", "position", "rotation"]
	__optional__ = ["properties"]
	__required_types__ = ["enum", "uint32", "Point3", "Quat"]
	__optional_types__ = ["Property"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"properties": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.type = 0
		self.use_direction = 0
		self.position = Point3()
		self.rotation = Quat()
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['Modifier'] = Modifier
		
		


class ParticleFX:
	__required__ = []
	__optional__ = ["emitters", "modifiers"]
	__required_types__ = []
	__optional_types__ = ["Emitter", "Modifier"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"emitters": [], "modifiers": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['ParticleFX'] = ParticleFX
		
		


class SplinePoint:
	__required__ = ["x", "y", "t_x", "t_y"]
	__optional__ = []
	__required_types__ = ["float", "float", "float", "float"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.x = 0.0
		self.y = 0.0
		self.t_x = 0.0
		self.t_y = 0.0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['SplinePoint'] = SplinePoint
		
		


class ClearColor:
	__required__ = ["color"]
	__optional__ = []
	__required_types__ = ["Vector4"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.color = Vector4()
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['ClearColor'] = ClearColor
		
		


class DisplayProfile:
	__required__ = ["name"]
	__optional__ = ["qualifiers"]
	__required_types__ = ["string"]
	__optional_types__ = ["DisplayProfileQualifier"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"qualifiers": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.name = ""
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['DisplayProfile'] = DisplayProfile
		
		


class DisplayProfileQualifier:
	__required__ = ["width", "height"]
	__optional__ = ["device_models"]
	__required_types__ = ["uint32", "uint32"]
	__optional_types__ = ["string"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"device_models": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.width = 0
		self.height = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['DisplayProfileQualifier'] = DisplayProfileQualifier
		
		


class DisplayProfiles:
	__required__ = []
	__optional__ = ["profiles"]
	__required_types__ = []
	__optional_types__ = ["DisplayProfile"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"profiles": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['DisplayProfiles'] = DisplayProfiles
		
		


class DrawDebugText:
	__required__ = ["position", "text", "color"]
	__optional__ = []
	__required_types__ = ["Point3", "string", "Vector4"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.position = Point3()
		self.text = ""
		self.color = Vector4()
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['DrawDebugText'] = DrawDebugText
		
		


class DrawLine:
	__required__ = ["start_point", "end_point", "color"]
	__optional__ = []
	__required_types__ = ["Point3", "Point3", "Vector4"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.start_point = Point3()
		self.end_point = Point3()
		self.color = Vector4()
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['DrawLine'] = DrawLine
		
		


class DrawText:
	__required__ = ["position", "text"]
	__optional__ = []
	__required_types__ = ["Point3", "string"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.position = Point3()
		self.text = ""
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['DrawText'] = DrawText
		
		


class FontDesc:
	__required__ = ["font", "material", "size", "antialias", "alpha", "outline_alpha", "outline_width", "shadow_alpha", "shadow_blur", "shadow_x", "shadow_y", "extra_characters", "output_format", "all_chars", "cache_width", "cache_height", "render_mode", "characters"]
	__optional__ = []
	__required_types__ = ["string", "string", "uint32", "uint32", "float", "float", "float", "float", "uint32", "float", "float", "string", "enum", "bool", "uint32", "uint32", "enum", "string"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.font = ""
		self.material = ""
		self.size = 0
		self.antialias = 1
		self.alpha = 1.0
		self.outline_alpha = 0.0
		self.outline_width = 0.0
		self.shadow_alpha = 0.0
		self.shadow_blur = 0
		self.shadow_x = 0.0
		self.shadow_y = 0.0
		self.extra_characters = ""
		self.output_format = 0
		self.all_chars = False
		self.cache_width = 0
		self.cache_height = 0
		self.render_mode = 0
		self.characters = ""
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['FontDesc'] = FontDesc
		
		


class FontMap:
	__required__ = ["glyph_bank", "material", "shadow_x", "shadow_y", "alpha", "outline_alpha", "shadow_alpha", "layer_mask"]
	__optional__ = []
	__required_types__ = ["string", "string", "float", "float", "float", "float", "float", "uint32"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.glyph_bank = ""
		self.material = ""
		self.shadow_x = 0.0
		self.shadow_y = 0.0
		self.alpha = 1.0
		self.outline_alpha = 1.0
		self.shadow_alpha = 1.0
		self.layer_mask = 1
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['FontMap'] = FontMap
		
		


class GlyphBank:
	__required__ = ["glyph_padding", "glyph_channels", "glyph_data", "max_ascent", "max_descent", "image_format", "sdf_spread", "sdf_offset", "sdf_outline", "sdf_shadow", "cache_width", "cache_height", "cache_cell_width", "cache_cell_height", "cache_cell_max_ascent", "padding", "is_monospaced"]
	__optional__ = ["glyphs"]
	__required_types__ = ["uint64", "uint32", "bytes", "float", "float", "enum", "float", "float", "float", "float", "uint32", "uint32", "uint32", "uint32", "uint32", "uint32", "bool"]
	__optional_types__ = ["Glyph"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"glyphs": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.glyph_padding = 0
		self.glyph_channels = 0
		self.glyph_data = ""
		self.max_ascent = 0.0
		self.max_descent = 0.0
		self.image_format = 0
		self.sdf_spread = 1.0
		self.sdf_offset = 0.0
		self.sdf_outline = 0.0
		self.sdf_shadow = 0.0
		self.cache_width = 0
		self.cache_height = 0
		self.cache_cell_width = 0
		self.cache_cell_height = 0
		self.cache_cell_max_ascent = 0
		self.padding = 0
		self.is_monospaced = False
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['GlyphBank'] = GlyphBank
		
		


class MaterialDesc:
	__required__ = ["name", "vertex_program", "fragment_program", "vertex_space", "max_page_count"]
	__optional__ = ["tags", "vertex_constants", "fragment_constants", "textures", "samplers", "attributes"]
	__required_types__ = ["string", "string", "string", "enum", "uint32"]
	__optional_types__ = ["string", "Constant", "Constant", "string", "Sampler", "VertexAttribute"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"tags": [], "vertex_constants": [], "fragment_constants": [], "textures": [], "samplers": [], "attributes": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.name = ""
		self.vertex_program = ""
		self.fragment_program = ""
		self.vertex_space = 0
		self.max_page_count = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['MaterialDesc'] = MaterialDesc
		
		


class RenderPrototypeDesc:
	__required__ = ["script"]
	__optional__ = ["materials", "render_resources"]
	__required_types__ = ["string"]
	__optional_types__ = ["MaterialDesc", "RenderResourceDesc"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"materials": [], "render_resources": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.script = ""
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['RenderPrototypeDesc'] = RenderPrototypeDesc
		
		


class Resize:
	__required__ = ["width", "height"]
	__optional__ = []
	__required_types__ = ["uint32", "uint32"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.width = 0
		self.height = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['Resize'] = Resize
		
		


class WindowResized:
	__required__ = ["width", "height"]
	__optional__ = []
	__required_types__ = ["uint32", "uint32"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.width = 0
		self.height = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['WindowResized'] = WindowResized
		
		


class HashDigest:
	__required__ = ["data"]
	__optional__ = []
	__required_types__ = ["bytes"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.data = ""
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['HashDigest'] = HashDigest
		
		


class ManifestData:
	__required__ = ["header"]
	__optional__ = ["engine_versions", "resources"]
	__required_types__ = ["ManifestHeader"]
	__optional_types__ = ["HashDigest", "ResourceEntry"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"engine_versions": [], "resources": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.header = ManifestHeader()
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['ManifestData'] = ManifestData
		
		


class ManifestFile:
	__required__ = ["data", "signature", "archive_identifier", "version"]
	__optional__ = []
	__required_types__ = ["bytes", "bytes", "bytes", "uint32"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.data = ""
		self.signature = ""
		self.archive_identifier = ""
		self.version = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['ManifestFile'] = ManifestFile
		
		


class ManifestHeader:
	__required__ = ["resource_hash_algorithm", "signature_hash_algorithm", "signature_sign_algorithm", "project_identifier"]
	__optional__ = []
	__required_types__ = ["enum", "enum", "enum", "HashDigest"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.resource_hash_algorithm = 3
		self.signature_hash_algorithm = 3
		self.signature_sign_algorithm = 1
		self.project_identifier = HashDigest()
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['ManifestHeader'] = ManifestHeader
		
		


class Reload:
	__required__ = []
	__optional__ = ["resources"]
	__required_types__ = []
	__optional_types__ = ["string"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"resources": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['Reload'] = Reload
		
		


class ResourceEntry:
	__required__ = ["hash", "url", "url_hash", "size", "compressed_size", "flags"]
	__optional__ = ["dependants"]
	__required_types__ = ["HashDigest", "string", "uint64", "uint32", "uint32", "uint32"]
	__optional_types__ = ["uint64"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"dependants": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.hash = HashDigest()
		self.url = ""
		self.url_hash = 0
		self.size = 0
		self.compressed_size = 0
		self.flags = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['ResourceEntry'] = ResourceEntry
		
		


class AnimationInstanceDesc:
	__required__ = ["animation"]
	__optional__ = []
	__required_types__ = ["string"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.animation = ""
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['AnimationInstanceDesc'] = AnimationInstanceDesc
		
		


class AnimationSet:
	__required__ = []
	__optional__ = ["animations"]
	__required_types__ = []
	__optional_types__ = ["RigAnimation"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"animations": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['AnimationSet'] = AnimationSet
		
		


class AnimationSetDesc:
	__required__ = ["skeleton"]
	__optional__ = ["animations"]
	__required_types__ = ["string"]
	__optional_types__ = ["AnimationInstanceDesc"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"animations": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.skeleton = ""
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['AnimationSetDesc'] = AnimationSetDesc
		
		


class AnimationTrack:
	__required__ = ["bone_id"]
	__optional__ = ["positions", "rotations", "scale"]
	__required_types__ = ["uint64"]
	__optional_types__ = ["float", "float", "float"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"positions": [], "rotations": [], "scale": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.bone_id = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['AnimationTrack'] = AnimationTrack
		
		


class Bone:
	__required__ = ["parent", "id", "name", "local", "world", "inverse_bind_pose", "length"]
	__optional__ = []
	__required_types__ = ["uint32", "uint64", "string", "Transform", "Transform", "Transform", "float"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.parent = 0
		self.id = 0
		self.name = ""
		self.local = Transform()
		self.world = Transform()
		self.inverse_bind_pose = Transform()
		self.length = 0.0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['Bone'] = Bone
		
		


class EventKey:
	__required__ = ["t", "integer", "float", "string"]
	__optional__ = []
	__required_types__ = ["float", "int32", "float", "uint64"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.t = 0.0
		self.integer = 0
		self.float = 0.0
		self.string = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['EventKey'] = EventKey
		
		


class EventTrack:
	__required__ = ["event_id"]
	__optional__ = ["keys"]
	__required_types__ = ["uint64"]
	__optional_types__ = ["EventKey"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"keys": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.event_id = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['EventTrack'] = EventTrack
		
		


class IK:
	__required__ = ["id", "parent", "child", "target", "positive", "mix"]
	__optional__ = []
	__required_types__ = ["uint64", "uint32", "uint32", "uint32", "bool", "float"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.id = 0
		self.parent = 0
		self.child = 0
		self.target = 0
		self.positive = True
		self.mix = 1.0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['IK'] = IK
		
		


class Mesh:
	__required__ = ["aabb_min", "aabb_max", "num_texcoord0_components", "num_texcoord1_components", "indices", "indices_format", "material_index"]
	__optional__ = ["positions", "normals", "tangents", "colors", "texcoord0", "texcoord1", "weights", "bone_indices"]
	__required_types__ = ["Vector3", "Vector3", "uint32", "uint32", "bytes", "enum", "uint32"]
	__optional_types__ = ["float", "float", "float", "float", "float", "float", "float", "uint32"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"positions": [], "normals": [], "tangents": [], "colors": [], "texcoord0": [], "texcoord1": [], "weights": [], "bone_indices": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.aabb_min = Vector3()
		self.aabb_max = Vector3()
		self.num_texcoord0_components = 0
		self.num_texcoord1_components = 0
		self.indices = ""
		self.indices_format = 0
		self.material_index = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['Mesh'] = Mesh
		
		


class MeshSet:
	__required__ = ["max_bone_count"]
	__optional__ = ["models", "materials", "bone_list"]
	__required_types__ = ["uint32"]
	__optional_types__ = ["Model", "string", "uint64"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"models": [], "materials": [], "bone_list": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.max_bone_count = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['MeshSet'] = MeshSet
		
		


class RigAnimation:
	__required__ = ["id", "duration", "sample_rate"]
	__optional__ = ["tracks", "event_tracks"]
	__required_types__ = ["uint64", "float", "float"]
	__optional_types__ = ["AnimationTrack", "EventTrack"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"tracks": [], "event_tracks": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.id = 0
		self.duration = 0.0
		self.sample_rate = 0.0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['RigAnimation'] = RigAnimation
		
		


class RigScene:
	__required__ = ["skeleton", "animation_set", "mesh_set", "texture_set"]
	__optional__ = []
	__required_types__ = ["string", "string", "string", "string"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.skeleton = ""
		self.animation_set = ""
		self.mesh_set = ""
		self.texture_set = ""
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['RigScene'] = RigScene
		
		


class Skeleton:
	__required__ = []
	__optional__ = ["bones", "iks"]
	__required_types__ = []
	__optional_types__ = ["Bone", "IK"]
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {"bones": [], "iks": []}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['Skeleton'] = Skeleton
		
		


class Exit:
	__required__ = ["code"]
	__optional__ = []
	__required_types__ = ["int32"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.code = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['Exit'] = Exit
		
		


class LuaRef:
	__required__ = ["ref", "context_table_ref"]
	__optional__ = []
	__required_types__ = ["int32", "int32"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.ref = 0
		self.context_table_ref = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['LuaRef'] = LuaRef
		
		


class LuaSource:
	__required__ = ["script", "filename", "bytecode", "delta", "bytecode_32", "bytecode_64"]
	__optional__ = []
	__required_types__ = ["bytes", "string", "bytes", "bytes", "bytes", "bytes"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.script = ""
		self.filename = ""
		self.bytecode = ""
		self.delta = ""
		self.bytecode_32 = ""
		self.bytecode_64 = ""
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['LuaSource'] = LuaSource
		
		


class Reboot:
	__required__ = ["arg1", "arg2", "arg3", "arg4", "arg5", "arg6"]
	__optional__ = []
	__required_types__ = ["string", "string", "string", "string", "string", "string"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.arg1 = ""
		self.arg2 = ""
		self.arg3 = ""
		self.arg4 = ""
		self.arg5 = ""
		self.arg6 = ""
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['Reboot'] = Reboot
		
		


class SetUpdateFrequency:
	__required__ = ["frequency"]
	__optional__ = []
	__required_types__ = ["int32"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.frequency = 0
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['SetUpdateFrequency'] = SetUpdateFrequency
		
		


class SetVsync:
	__required__ = ["swap_interval"]
	__optional__ = []
	__required_types__ = ["int32"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.swap_interval = 1
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['SetVsync'] = SetVsync
		
		


class StartRecord:
	__required__ = ["file_name", "frame_period", "fps"]
	__optional__ = []
	__required_types__ = ["string", "int32", "int32"]
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		self.file_name = ""
		self.frame_period = 2
		self.fps = 30
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['StartRecord'] = StartRecord
		
		


class StopRecord:
	__required__ = []
	__optional__ = []
	__required_types__ = []
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['StopRecord'] = StopRecord
		
		


class TogglePhysicsDebug:
	__required__ = []
	__optional__ = []
	__required_types__ = []
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['TogglePhysicsDebug'] = TogglePhysicsDebug
		
		


class ToggleProfile:
	__required__ = []
	__optional__ = []
	__required_types__ = []
	__optional_types__ = []
	__defold__ = getattr(Defold,__qualname__)
	__optional_defaults__ = {}
	
	def __init__(self, *args,**kwargs):
		self.before_init( *args,**kwargs)
		
		self.after_init( *args,**kwargs)


	def build_instance(self) : 
		instance = self.__defold__()
		args = dict()
		for var in vars(self) : 
			if (var in self.__required__) or (var in self.__optional__) : 
				_var = getattr(self,var) 
				if hasattr(_var,'to_dict') : 
					args[var] = _var.to_dict()
				elif hasattr(_var,'__iter__') and all(hasattr(i,'to_dict') for i in _var ) : 
					if not type(_var) is str : 
						args[var] = [i.to_dict() for i in _var  ]
					else : 
						args[var] = _var
				else : 
					args[var] = _var
		ParseDict(args,instance)
		return instance 

	def before_init(self,*args,**kwargs) : 
		pass 

	def after_init(self,*args,**kwargs) : 
		pass 

	def to_dict(self) : 
		instance = self.build_instance()
		return MessageToDict(instance , preserving_proto_field_name=True )

	def __getattr__(self, attr):
		print("Called on " , attr  , attr in self.__optional_defaults__ )
		if attr in self.__optional_defaults__ : 
			setattr(self,attr , self.__optional_defaults__.get(attr))
			return self.__getattribute__(attr)
		raise AttributeError(self.__qualname__  + " does not have attributte "  + str(attr))
	
	def __repr__(self) : 
		instance = self.build_instance()
		return MessageToString(instance)


	def update(self,_dict) : 
		for k , v in _dict.items()  : 
			if k in self.__required__ : 
				if hasattr(Defold,k) : 
					_typ = self.__required_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)
			if k in self.__optional__ : 
				if hasattr(Defold,k) : 
					_typ = self.__optional_types__[self.__required__.index(k)]
					sub_member = getattr(DefoldApi,_typ)()
					sub.update(v)
					setattr(self,k,sub_member)
				else : 
					setattr(self,k,v)

			

DefoldApi['ToggleProfile'] = ToggleProfile
		
		



DefoldApi = collections.namedtuple('DefoldApi' , DefoldApi.keys() )(**DefoldApi)
__all__ = ['DefoldApi']

