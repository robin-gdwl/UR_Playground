mir_stops = [0.1,0.6,1]
mir_opac = [1,2,3]
mir_colors = [[0,1,2],[2,3,4],[3,5,6]]

mir_stops.reverse()
mir_opac.reverse()
mir_colors.reverse()

for i, stop_off in enumerate(mir_stops):
    mir_stops[i] = (1 - stop_off) / 2

mir_stops_reverse = mir_stops[::-1]
for i, stop_off in enumerate(mir_stops_reverse):
    mir_stops_reverse[i] = 1 - stop_off

mir_stops.extend(mir_stops_reverse)
mir_opac.extend(mir_opac[::-1])
mir_colors.extend(mir_colors[::-1])

grad_stop_offsets = mir_stops
grad_opacities = mir_opac
grad_colors = mir_colors

print(grad_stop_offsets)
print(grad_opacities)
print(grad_colors)