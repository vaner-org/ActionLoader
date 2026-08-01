bl_info = {
	"name": "Action Loader",
	"author": "Frederico Martins, modified by vaner",
	"version": (5, 0),
	"blender": (4, 0, 2),
	"location": "View3D > Tools > Animation",
	"description": "Toolbars for smoother management of Actions",
	"warning": "",
	"wiki_url": "https://github.com/vaner-org/ActionLoader",
	"tracker_url": "https://github.com/vaner-org/ActionLoader/issues",
	"category": "Animation",
	}

import bpy
import inspect
import sys
global extra_info
extra_info = False

filter_name = ''
filter_name2 = ''


def set_prevspeed(self, value):
	global prev_mode 
	global old_prevspeed 
	old_prevspeed = bpy.context.scene.actionloader_speedprev
	if bpy.context.scene.actionloader_speedprev == "0":
		#print ("ZERO")
		prev_mode = bpy.context.scene.use_preview_range
	self["testprop"] = value
	
  
def get_prevspeed(self):
	#print("get")
	try:
		return self["testprop"];
	except:
		return 0;
	
def update_prevspeed(self, context):
	speed = bpy.context.scene.actionloader_speedprev
	
	print("SPEEDCHANGE")
	ob = context.active_object
	scn = context.scene
	ActiveAction = ob.animation_data.action
		
	if scn.actionloader_rangemode == "0":
		sframe = int(ActiveAction["frame_start"])
		eframe = int(ActiveAction["frame_end"])
	else:
		sframe = int(ActiveAction.frame_range[0])
		eframe = int(ActiveAction.frame_range[1])
	
	if speed == "0":
		scn.frame_start = sframe
		scn.frame_end = eframe
		scn.render.frame_map_new = 100
		if old_prevspeed == "1":
			scn.frame_current = int(scn.frame_current / 2 )
		elif old_prevspeed == "2":
			scn.frame_current =  int(scn.frame_current / 4 )
		elif old_prevspeed == "3":
			scn.frame_current =  int(scn.frame_current / 8)
		scn.use_preview_range = prev_mode
		
	elif speed == "1":
		scn.frame_start = sframe*2
		scn.frame_end = eframe*2
		scn.render.frame_map_new = 200
		if old_prevspeed == "0":
			scn.frame_current =  int(scn.frame_current * 2)
		elif old_prevspeed == "2":
			scn.frame_current =  int(scn.frame_current / 2 )
		elif old_prevspeed == "3":
			scn.frame_current =  int(scn.frame_current / 4 )
		scn.use_preview_range = False
	
	elif speed == "2":
		scn.frame_start = sframe*4
		scn.frame_end = eframe*4
		scn.render.frame_map_new = 400
		if old_prevspeed == "0":
			scn.frame_current =  int(scn.frame_current * 4)
		elif old_prevspeed == "1":
			scn.frame_current =  int(scn.frame_current * 2)
		elif old_prevspeed == "3":
			scn.frame_current =  int(scn.frame_current / 2)
		scn.use_preview_range = False
	
	elif speed == "3":
		scn.frame_start = sframe*8
		scn.frame_end = eframe*8
		scn.render.frame_map_new = 800
		if old_prevspeed == "0":
			scn.frame_current =  int(scn.frame_current * 8)
		elif old_prevspeed == "1":
			scn.frame_current =  int(scn.frame_current * 4)
		elif old_prevspeed == "2":
			scn.frame_current =  int(scn.frame_current * 2)
		scn.use_preview_range = False
	

def set_normal_speed():
	scn = bpy.context.scene
	if bpy.context.object == None or bpy.context.object.animation_data == None or bpy.context.object.animation_data.action == None:
		pass
	else:
		ActiveAction = bpy.context.active_object.animation_data.action
		if ActiveAction.get("frame_start") != None:
			scn.frame_start = int(ActiveAction["frame_start"])
			scn.frame_end = int(ActiveAction["frame_end"])
		else:
			scn.frame_start = int(ActiveAction.frame_range[0])
			scn.frame_end = int(ActiveAction.frame_range[1]) 

	scn.use_preview_range = prev_mode
	scn.actionloader_speedprev = '0'
	scn.render.frame_map_new = 100
 

def update_action_list(self, context):
	#updates every time you pick action in the list
	ob = context.active_object
	#ob = context.object
	scn = context.scene
	if scn.render.frame_map_new != 100:
		set_normal_speed()

	if ob.animation_data == None:
		action = 0 # No Animation data
	elif ob.animation_data.action == None:
		action = 1 # No Action
	else:
		action = 2 # Has Action

	if action == 2: # Has action
		ob.animation_data.action.use_fake_user = True
	elif action == 0: # No Animation data
		ob.animation_data_create()

	# Apply reset action first if enabled
	if scn.actionloader_useReset and scn.actionloader_resetAction:
		ob.animation_data.action = scn.actionloader_resetAction
		# Update the scene to apply the reset action
		bpy.context.view_layer.update()

	#then change the action to the picked on the list
	ob.animation_data.action = bpy.data.actions[ob.action_list_index]

	ActiveAction = context.active_object.animation_data.action
	ActiveAction.use_fake_user = True

	# Changes the range on the scene
	if scn.actionloader_autorange:
		# Use the range mode to determine which operator to call
		if scn.actionloader_rangemode == "1":
			bpy.ops.setkeyframerange.action()
		else:
			bpy.ops.setmanualrange.action()

	if scn.actionloader_1stFrame== True:
		scn.frame_current = scn.frame_start 

		"""
		#center stuff on dopesheet etc...
		for area in context.screen.areas:
			if area.type == 'DOPESHEET_EDITOR':
				for region in area.regions:
					if region.type == 'WINDOW':
						override = {'area': area, 'region': region, 'edit_object': context.edit_object}
						bpy.ops.action.view_all(override)
						
			elif area.type == 'GRAPH_EDITOR':
				for region in area.regions:
					if region.type == 'WINDOW':
						override = {'area': area, 'region': region, 'edit_object': context.edit_object}
						bpy.ops.graph.view_all(override)
			
			elif area.type == 'TIMELINE':
				for region in area.regions:
					if region.type == 'WINDOW':
						override = {'area': area, 'region': region, 'edit_object': context.edit_object}
						bpy.ops.time.view_all(override)    

		"""
		
class ACTION_UL_list2(bpy.types.UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
		self.use_filter_show = True
		ob = bpy.context.active_object
		#ob = bpy.context.object
		if self.layout_type in {'DEFAULT', 'COMPACT'}:
			layout.prop(item, "name", text="", emboss=False)
				#layout.operator("delete.action", text="", icon = "ERROR").delaction = bpy.data.actions[ob.action_list_index].name
				#layout.operator("ttt.action", text ="T").nome = str(self._DATA)
				#layout.label(text = "", icon = "ERROR")
		elif self.layout_type in {'GRID'}:
			pass
		global filter_name2
		filter_name2 = self.filter_name
		
class ACTION_UL_list(bpy.types.UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
		self.use_filter_show = True
		
		try:
			if "frame_end" in item and "frame_start" in item:
				durationf = item["frame_end"] - item["frame_start"]
			else:
				durationf = item.frame_range[1] - item.frame_range[0]
		except:
			durationf = 0
		durations = durationf / bpy.context.scene.render.fps if durationf > 0 else 0
			
		# Draw Info!  
		durations = durationf / bpy.context.scene.render.fps 
		info2 = str(durationf)+ " f. | "+ str(round(durations,6))+ " s. "
		
		
		if item.use_fake_user == True:
			fakeuser = "F"
		else:
			fakeuser = "X"
		
		info = str(item.users)+ fakeuser + " | " + str(len(item.pose_markers)) + "m | " + str(durationf) + "f | "+ str(round(durations,6))+ "s"
						
		if self.layout_type in {'DEFAULT', 'COMPACT'}:
			layout.prop(item, "name", text="", emboss=False)
			if extra_info:
				layout.label(text = info)
			
		elif self.layout_type in {'GRID'}:
			pass
		global filter_name
		filter_name = self.filter_name


class ActionLoaderPanel(bpy.types.Panel):
	"""Creates a Panel in the Animation tab of the 3D View's Tools"""
	bl_label = "Actions"
	bl_idname = "OBJECT_PT_action_loader"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Actions"
	bl_order = 1
	
	def draw(self, context):
		layout = self.layout
		scn = context.scene
		ob = context.active_object

		if context.active_object != None:
			list_context = ob
		else:
			list_context = scn

		# Show action name and controls at the top if object has an action
		if ob and ob.animation_data and ob.animation_data.action:
			AA = ob.animation_data.action
			row = layout.row(align=True)

			# Check if action list is out of sync
			if ob.action_list_index > (len(bpy.data.actions)-1) or bpy.data.actions[ob.action_list_index] != ob.animation_data.action:
				row.operator("sync.action", icon = "FILE_REFRESH", text="Sync Action")
			else:
				row.label(text = AA.name)
				row.operator("makeexclusive.action", icon = "SOLO_ON")
				row.operator("duplicate.action", icon = "DUPLICATE")
				row.operator("unlinks.action", icon = "X")
				row.operator("delete.action", text="", icon="TRASH")

		#UIList - no object
		row = layout.row(align=True)
		row.template_list("ACTION_UL_list", "", bpy.data, "actions", list_context, "action_list_index")
		if bpy.context.scene.actionloader_DualView:
			row.template_list("ACTION_UL_list2", "", bpy.data, "actions", list_context, "action_list_index")

		# DUAL VIEW BUTTON
		if scn.actionloader_DualView:
			dual_icon = "TRACKING_CLEAR_BACKWARDS"
			dual_text = "Single View"
		else:
			dual_icon = "MOD_ARRAY"
			dual_text = "Split View"
		layout.prop(scn, 'actionloader_DualView', text=dual_text, icon=dual_icon)


class ActionLoaderPlaybackPanel(bpy.types.Panel):
	"""Playback Options Panel"""
	bl_label = "Playback"
	bl_idname = "OBJECT_PT_action_loader_playback"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Actions"
	bl_order = 0
	bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):
		layout = self.layout
		ob = context.active_object

		# Display frame and time info at the top only if action exists
		if ob and ob.animation_data and ob.animation_data.action:
			AA = ob.animation_data.action
			try:
				if "frame_end" in AA and "frame_start" in AA:
					durationf = AA["frame_end"] - AA["frame_start"]
				else:
					durationf = AA.frame_range[1] - AA.frame_range[0]
			except:
				durationf = 0
			durations = durationf / context.scene.render.fps if durationf > 0 else 0
			frames_text = str(int(durationf)) + " frames"
			seconds_text = str(round(durations, 2)) + " sec"

			split = layout.split(factor=0.5, align=True)
			split.label(text = frames_text, icon = "ACTION")
			row = split.row(align=True)
			row.alignment = 'RIGHT'
			row.label(text = "", icon = "TIME")
			row.label(text = seconds_text)

		layout.label(text = "Playback Speed:")
		row = layout.row()
		row.prop(context.scene, 'actionloader_speedprev', expand=True)

		layout.label(text = "Set frame range to:")
		row = layout.row(align=True)
		row.operator("setmanualrange.action", text="Manual")
		row.operator("setkeyframerange.action", text="Keyframes")


class ActionLoaderOnSelectionPanel(bpy.types.Panel):
	"""Selection Options Panel"""
	bl_label = "Selection"
	bl_idname = "OBJECT_PT_action_loader_on_selection"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Actions"
	bl_order = 2
	bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):
		layout = self.layout
		scn = context.scene

		layout.prop(scn, "actionloader_autorange", text="Set range automatically")
		layout.prop(scn, "actionloader_1stFrame", text="Jump to first frame")
		layout.prop(scn, "actionloader_useReset", text="Apply reset action first")
		if scn.actionloader_useReset:
			layout.prop(scn, "actionloader_resetAction", text="")


class OBJECT_OT_DuplicateAction(bpy.types.Operator):
	"""Duplicate action"""
	bl_idname = "duplicate.action"
	bl_label = ""
	
	def execute(self, context):
		scn = bpy.context.scene
		ob = context.active_object
		if ob and ob.animation_data and ob.animation_data.action:
			ob.animation_data.action.use_fake_user = True
		if ob == None:
			newAnim = bpy.data.actions[scn.action_list_index].copy()
		else:
			newAnim = bpy.data.actions[bpy.context.object.action_list_index].copy()
			ob.animation_data.action = newAnim
			quickfix_index()
		return{'FINISHED'}   


class OBJECT_OT_UnlinkAction(bpy.types.Operator):
	"""Unlink action from active object"""
	bl_idname = "unlinks.action"
	bl_label = ""

	def execute(self, context):
		ob = context.active_object
		if ob.animation_data and ob.animation_data.action:
			ob.animation_data.action.use_fake_user = True
			ob.animation_data.action = None
		return{'FINISHED'}


class OBJECT_OT_MakeExclusive(bpy.types.Operator):
	"""Unlink action from all users other than the active object"""
	bl_idname = "makeexclusive.action"
	bl_label = ""

	def execute(self, context):
		ob = context.active_object
		if not ob or not ob.animation_data or not ob.animation_data.action:
			return {'CANCELLED'}

		current_action = ob.animation_data.action

		# Unlink from all other objects
		for obj in bpy.data.objects:
			if obj != ob and obj.animation_data and obj.animation_data.action == current_action:
				obj.animation_data.action = None

		# Unlink from NLA strips in all objects (including the active object)
		for obj in bpy.data.objects:
			if obj.animation_data and obj.animation_data.nla_tracks:
				for track in obj.animation_data.nla_tracks:
					for strip in track.strips:
						if strip.action == current_action:
							track.strips.remove(strip)

		# Unlink from scene sequence editor strips
		if bpy.context.scene.sequence_editor:
			for seq in bpy.context.scene.sequence_editor.sequences_all:
				if hasattr(seq, 'action') and seq.action == current_action:
					seq.action = None

		return{'FINISHED'}


class OBJECT_OT_fixsync(bpy.types.Operator):
	"""Sync action with Dope Sheet selection"""
	bl_idname = "sync.action"
	bl_label = "Sync"
	
	def execute(self, context):
		quickfix_index()
		return{'FINISHED'}  


class OBJECT_OT_SetManualRange(bpy.types.Operator):
	"""Set frame range using manual custom properties"""
	bl_idname = "setmanualrange.action"
	bl_label = "Set Manual Range"

	def execute(self, context):
		ob = context.active_object
		scn = context.scene
		if not ob or not ob.animation_data or not ob.animation_data.action:
			return {'FINISHED'}

		ActiveAction = ob.animation_data.action

		# Set to manual mode
		scn.actionloader_rangemode = "0"

		# Use custom properties if they exist, otherwise use keyframe range
		if ActiveAction.get("frame_start") is not None:
			scn.frame_preview_start = int(ActiveAction["frame_start"])
			scn.frame_preview_end = int(ActiveAction["frame_end"])
			scn.frame_start = int(ActiveAction["frame_start"])
			scn.frame_end = int(ActiveAction["frame_end"])
		else:
			# Use keyframe range directly (don't create custom properties)
			scn.frame_preview_start = int(ActiveAction.frame_range[0])
			scn.frame_preview_end = int(ActiveAction.frame_range[1])
			scn.frame_start = int(ActiveAction.frame_range[0])
			scn.frame_end = int(ActiveAction.frame_range[1])

		return{'FINISHED'}


class OBJECT_OT_SetKeyframeRange(bpy.types.Operator):
	"""Set frame range using actual keyframe positions"""
	bl_idname = "setkeyframerange.action"
	bl_label = "Set Keyframe Range"

	def execute(self, context):
		ob = context.active_object
		scn = context.scene
		if not ob or not ob.animation_data or not ob.animation_data.action:
			self.report({'WARNING'}, "No action found")
			return {'CANCELLED'}

		ActiveAction = ob.animation_data.action

		# Get the actual keyframe range by calculating from fcurves
		if len(ActiveAction.fcurves) == 0:
			self.report({'WARNING'}, "Action has no keyframes")
			return {'CANCELLED'}

		start_frame = None
		end_frame = None

		for fcurve in ActiveAction.fcurves:
			for keyframe in fcurve.keyframe_points:
				frame = keyframe.co[0]
				if start_frame is None or frame < start_frame:
					start_frame = frame
				if end_frame is None or frame > end_frame:
					end_frame = frame

		if start_frame is None or end_frame is None:
			self.report({'WARNING'}, "Could not determine keyframe range")
			return {'CANCELLED'}

		start_frame = int(start_frame)
		end_frame = int(end_frame)

		# Set to keyframes mode
		scn.actionloader_rangemode = "1"

		# Use actual keyframe range
		scn.frame_preview_start = start_frame
		scn.frame_preview_end = end_frame
		scn.frame_start = start_frame
		scn.frame_end = end_frame

		return{'FINISHED'} 


class OBJECT_OT_DeleteAction(bpy.types.Operator):
	"""Delete action from file."""
	bl_idname = "delete.action"
	bl_label = ""
	#delaction = bpy.props.StringProperty()
	def execute(self, context):
		#set_normal_speed()
		if not bpy.data.actions:
			return {'FINISHED'}

		ob = context.active_object
		if ob == None:
			ActionNR = context.scene.action_list_index
		else:
			ActionNR = context.object.action_list_index
		AA = bpy.data.actions[ActionNR] 
		
		if ob:
			ob.action_list_index = bpy.context.object.action_list_index-1
		else:
			bpy.context.scene.action_list_index = bpy.context.scene.action_list_index-1    
		
		bpy.data.actions.remove(AA, do_unlink=True)
		return{'FINISHED'} 
  
	
def quickfix_index():
  
	for x in range(len(bpy.data.actions)): 
		if bpy.data.actions[x] == bpy.context.object.animation_data.action:
			bpy.context.object.action_list_index = x  


def register():
	bpy.types.Scene.actionloader_DualView = bpy.props.BoolProperty(default= False, description = "Two List of the Actions so you can have different filters on each. Doesn't affect or change anything in the scene, just for listing.")
	
	bpy.types.Object.action_list_index = bpy.props.IntProperty(
		override={"LIBRARY_OVERRIDABLE"}, 
		update = update_action_list, 
		description = "Action Loader's highlighted action on list for this object"
		)
	bpy.types.Scene.action_list_index = bpy.props.IntProperty(
		#update = update_action_list_noObj, 
		description = "Action Loader's highlighted action on list for this scene when no object selected"
		)
	enum_items = (
		('0','Manual','Sets Frame Range of action by the manually set Frame Range'),
		('1','Keyframes',"Sets Frame Range by action's first and last keyframe")
		)
	bpy.types.Scene.actionloader_rangemode = bpy.props.EnumProperty(
		items = enum_items,
		description = "Set the range for 0: manual or 1: based on keyframes"
		)
	enum_prevspeed = (
		('0','Normal','Set speed to Normal (Time Remapping "frame_map_new" to 100 and adjusts range)'),
		('1','1/2', 'Set speed to half (Time Remapping "frame_map_new" to 200 and adjusts range)'),
		('2','1/4', 'Set speed to a quarter (Time Remapping "frame_map_new" to 400 and adjusts range)'),
		('3','1/8', 'Set speed to an eighth (Time Remapping "frame_map_new" to 800 and adjusts range)')
		)
	bpy.types.Scene.actionloader_speedprev = bpy.props.EnumProperty(
		items = enum_prevspeed,
		update=update_prevspeed, 
		set = set_prevspeed, 
		get = get_prevspeed
		)
	bpy.types.Scene.actionloader_autorange = bpy.props.BoolProperty(
		name = "Set playback range automatically",
		description = "Automatically set the timeline range when switching actions",
		default = False
		)
	bpy.types.Scene.actionloader_1stFrame = bpy.props.BoolProperty(
		name = "Jump to first frame",
		description = "Automatically move playhead to the first frame when switching actions",
		default = False
		)
	bpy.types.Scene.actionloader_useReset = bpy.props.BoolProperty(
		name = "Apply reset action first",
		description = "Apply a reset action before switching to the selected action",
		default = False
		)
	bpy.types.Scene.actionloader_resetAction = bpy.props.PointerProperty(
		type = bpy.types.Action,
		name = "Reset Action",
		description = "The action to apply before switching to another action"
		)

	module_classes = inspect.getmembers(sys.modules[__name__], inspect.isclass)
	for cls in module_classes:
		bpy.utils.register_class(cls[1])


def unregister():
	module_classes = inspect.getmembers(sys.modules[__name__], inspect.isclass)
	for cls in module_classes:
		bpy.utils.unregister_class(cls[1])

	del bpy.types.Object.action_list_index
	del bpy.types.Scene.action_list_index
	del bpy.types.Scene.actionloader_autorange
	del bpy.types.Scene.actionloader_speedprev
	del bpy.types.Scene.actionloader_1stFrame
	del bpy.types.Scene.actionloader_useReset
	del bpy.types.Scene.actionloader_resetAction


if __name__ == "__main__":
	register()
	
