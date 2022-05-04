import cadquery as cq

# BEGIN PARAMS
#------------------

length = 90.0
width = 65
height = 25

shell_thickness = 2

# Space to leave for parts that fit together
# adjust for 3d printing or if you want to add a gasket
fitment_epsilon = 0.1

button_diam = 12.5
button_offset = 18

screw_post_diam = 4
screw_hole_size = 2.5 #M3 Bolt

# wiring port dimensions
wire_port_offset = (16, 4)
wire_port_width = 5
wire_port_height = 2

# END PARAMS
#-----------------------
#BEGIN CALCS

lid_width = width + (shell_thickness * 2)
lid_length = length + (shell_thickness * 2)

screw_post_rect = (
    width - (screw_post_diam / 2 + shell_thickness), 
    length - (screw_post_diam / 2 + shell_thickness)
)


#END CALCS
#-----------------------

base = cq.Workplane("front")\
    .box(width, length, height)\
    .faces("+Z").shell(shell_thickness)

# posts for screwing lid
base = base.faces("<Z").workplane(centerOption="CenterOfMass", offset=-shell_thickness)\
    .rect(screw_post_rect[0], screw_post_rect[1], forConstruction=True)\
    .vertices().circle(screw_post_diam).extrude(-height)\
    .rect(screw_post_rect[0], screw_post_rect[1], forConstruction=True)\
    .vertices().circle(screw_hole_size).cutBlind(-height)\

# Thru holes for wiring
base = base.faces(">Y").workplane(centerOption="CenterOfMass")\
    .rect(
        width - (wire_port_offset[0] + (wire_port_width / 2.0)), 
        height - (wire_port_offset[1] + (wire_port_height / 2.0)), 
        forConstruction=True
    ).vertices("<XZ")\
    .rect(wire_port_width, wire_port_height).cutBlind(-shell_thickness)

lid = base.faces(">Z").workplane(centerOption="CenterOfMass")\
    .box(lid_width, lid_length, 4, combine=False)\
    .edges("|Z").fillet(shell_thickness)\
    .faces("<Z").tag("rim")\
    .faces("<Z").workplane().box(
        width - (fitment_epsilon * 2), 
        length - (fitment_epsilon * 2), 
        shell_thickness / 2
    )\
    .faces("<Z").workplane()\
    .rect(screw_post_rect[0], screw_post_rect[1], forConstruction=True)\
    .vertices().circle(screw_post_diam).cutBlind(-shell_thickness / 2)\
    .faces(">Z").workplane()\
    .rect(screw_post_rect[0], screw_post_rect[1], forConstruction=True)\
    .vertices().cboreHole(screw_hole_size, 6.5, 3.1) # M3 socket head
    
# Lid top detail
lid = lid.faces(">Z").workplane()\
    .rect(
        lid_width - (button_offset * 2), 
        lid_length - (button_offset * 2), 
        forConstruction=True
    )\
    .vertices(">XY")\
    .hole(button_diam) 

# Render the solid

part = (
    cq.Assembly()
        .add(base, color=cq.Color("gray"), name="base")
        .add(lid, color=cq.Color("black"), name="lid")
)

(
    part
        .constrain("lid?rim", "base@faces@>Z", "Plane")
        .solve()
)

#Editor only
#show_object(part)

cq.exporters.export(base, "workBox.stl")
cq.exporters.export(lid, "workBoxLid.stl")

svgopt = {
    "showHidden": True,
    "showAxes": False
}

cq.exporters.export(base, "workBox.svg", opt=svgopt)
cq.exporters.export(lid, "workBoxLid.svg", opt=svgopt)