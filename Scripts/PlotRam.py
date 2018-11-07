import matplotlib.pyplot as plt
from matplotlib.legend_handler import HandlerPatch
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import numpy as np

class HandlerEllipse(HandlerPatch):
    def create_artists(self, legend, orig_handle,
                       xdescent, ydescent, width, height, fontsize, trans):
        center = 0.5 * width - 0.5 * xdescent, 0.5 * height - 0.5 * ydescent
        p = mpatches.Ellipse(xy=center, width=height + ydescent,
                             height=height + ydescent)
        self.update_prop(p, orig_handle, legend)
        p.set_transform(trans)
        return [p]


tamanhos = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]

# INTERNET
plt.plot(tamanhos, [7, 7, 7, 7, 7, 7, 8, 8, 7, 9, 9, 8, 8, 8, 8, 7, 8,  8,  7,  8, 9], '-bo')

# BOB
plt.plot(tamanhos, [7, 7, 7, 7, 7, 7, 8, 7, 8, 7, 7, 8, 8, 8, 9, 9, 10, 10, 10, 9, 10], '-ro')

# DIEL
plt.plot(tamanhos, [7, 7, 7, 7, 7, 7, 7, 8, 8, 7, 7, 7, 7, 8, 8, 9, 9,  10, 9,  10, 9], '-go')

# plt.plot(tamanhos, [1.96, 3, 27.94, 97.05], 'ro', label='Bob')
# plt.plot(tamanhos, [2.08, 3, 28.3, 98.59], 'go', label='Diel')


# Legendas:

# LAN Sync
lansync_result_bob_line = mpatches.Circle(0.5, 0.5, facecolor="red", label="Sem LS4MSN, com LAN Sync")
lansync_result_diel_line = mpatches.Circle(0.5, 0.5, facecolor="green", label="Com LS4MSN, com LAN Sync")

# Internet
internet_result_line = mpatches.Circle(0.5, 0.5, facecolor="blue", label='Sem LS4MSN, sem LAN Sync')

# Mostra legenda
plt.legend(handles=[lansync_result_bob_line, lansync_result_diel_line, internet_result_line],
    handler_map={mpatches.Circle: HandlerEllipse()})


plt.ylabel('Uso de RAM (%)')
plt.xlabel('Completude da operação (0-100%)')

plt.ylim(0, 100)

# plt.show()
plt.savefig('plot_ls4msn_ram.pdf')
