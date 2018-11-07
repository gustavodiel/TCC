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


tamanhos = [20, 40, 400, 1500]

test_range = np.arange(0., 1500, 0.05)

# Calcula teorico da Internet
plt.plot(test_range, test_range / 5, 'b--')

# Plota o obtido da Internet

cor_internet = 'bo'
plt.errorbar(tamanhos, [14.9, 26.1, 132.3, 413.45], yerr=[5.3, 10.14, 30.5, 36.4], fmt='bo')

# Calcula teorico da Rede local (25MB/s)
plt.plot(test_range, test_range / 25, 'r--', label='Line 3')

# Plota os resultados via LAN Sync obtidos

plt.errorbar(tamanhos, [1.46, 2.7, 26.94, 95.05], yerr=[0.2, 0.37, 0.39, 0.67], fmt='ro')


plt.errorbar(tamanhos, [2.08, 3, 28.3, 98.59], yerr=[0.14, 0.16, 0.35, 0.68], fmt='go')

# plt.plot(tamanhos, [1.96, 3, 27.94, 97.05], 'ro', label='Bob')
# plt.plot(tamanhos, [2.08, 3, 28.3, 98.59], 'go', label='Diel')


# Legendas:
# Teoricos:
lansync_theorical_line = mlines.Line2D([], [], color='red', linestyle='dashed', label='Tempo teórico desejado para conexão LAN Sync')
internet_theorical_line = mlines.Line2D([], [], color='blue', linestyle='dashed', label='Tempo teórico desejado para conexão via Internet')

# LAN Sync
lansync_result_bob_line = mpatches.Circle(0.5, 0.5, facecolor="red", label="Tempos com LAN Sync (Mesm sub-rede)")
lansync_result_diel_line = mpatches.Circle(0.5, 0.5, facecolor="green", label="Tempos com LAN Sync (Sub-redes diferentes)")

# Internet
internet_result_line = mpatches.Circle(0.5, 0.5, facecolor="blue", label='Tempos atingidos via Internet')

# Mostra legenda
plt.legend(handles=[internet_theorical_line, lansync_theorical_line, lansync_result_bob_line, lansync_result_diel_line, internet_result_line],
    handler_map={mpatches.Circle: HandlerEllipse()})


plt.ylabel('Tempo para sincronizar (s)')
plt.xlabel('Tamanho do arquivo (MB)')

# plt.show()
plt.savefig('plot_dropbox_comparacao_resultados_final.pdf')
