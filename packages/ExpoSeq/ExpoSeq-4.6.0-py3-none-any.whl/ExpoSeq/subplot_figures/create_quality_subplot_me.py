import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd
import numpy as np 
from ExpoSeq import plots
from ExpoSeq.plots.global_font import font_settings_normal, font_settings_title
from textwrap import wrap
import seaborn as sns
from matplotlib import cm
from matplotlib.colors import Normalize
from ExpoSeq.augment_data.loop_collect_reports import load_alignment_reports
import matplotlib
class PrepareData:
    
    @staticmethod
    def check_input(sequencing_report, region_of_interest, method):
        assert isinstance(sequencing_report, pd.DataFrame)
        assert type(region_of_interest) == str
        assert region_of_interest in sequencing_report.columns.to_list()
        assert type(method) == str
        assert method in ["Shannon", "InverseSimpson"]

    @staticmethod
    def calc_simpson_index(clones):
        return 1 / (np.sum(clones**2))

    @staticmethod
    def calc_shannon_index(clones):
        return -np.sum(clones * np.log(clones))

    def cleaning(self, sequencing_report, region_of_interest, method):
        self.check_input(sequencing_report, region_of_interest, method)
        values = []
        unique_experiments = sequencing_report["Experiment"].unique().tolist()
        for experiment in unique_experiments:
            exp_spec = sequencing_report[sequencing_report["Experiment"] == experiment]
            aa_seqs = exp_spec[region_of_interest]
            clones = exp_spec["cloneFraction"]
            if method == "InverseSimpson":
                values.append(self.calc_simpson_index(clones))
            if method == "Shannon":
                values.append(self.calc_shannon_index(clones))
        return values, unique_experiments




class SummarizeReport:
    
    @staticmethod
    def _find_most_reads(report):
        grouped_report = report.groupby("Experiment")["readCount"].sum().reset_index()
        max_sample = grouped_report.loc[grouped_report['readCount'].idxmax()]
        sample = max_sample["Experiment"]
        count = max_sample["readCount"]
        return sample, count


        
    def create_summary(self, plot):
        plot.change_region("aaSeqCDR3")
        unique_clones_cdr3 = plot.sequencing_report["aaSeqCDR3"].nunique()
        no_samples = len(plot.experiments_list)
        highest_sample, count = self._find_most_reads(plot.sequencing_report)
        diversity_count, diversity_sample = PrepareData().cleaning(plot.sequencing_report, plot.region_of_interest, "InverseSimpson")
        max_value = max(diversity_count)
        highest_diversity_ix = diversity_count.index(max_value)
        highest_diversity_count = diversity_count[highest_diversity_ix]
        highest_diversity_sample = diversity_sample[highest_diversity_ix]
        min_value = min(diversity_count)
        lowest_diversity_ix = diversity_count.index(min_value)
        lowest_diversity_count = diversity_count[lowest_diversity_ix]
        lowest_diversity_sample = diversity_sample[lowest_diversity_ix]
        data = {
        'NGS Attribute': ['Unique clones CDR3 Total', 
                          'Number samples', 
                          'Sample with most reads',
                          "Sample with highest diversity",
                          "Sample with lowest diversity",
                          ],
        'Value': [unique_clones_cdr3, 
                  no_samples, 
                  highest_sample, 
                  highest_diversity_sample, 
                  lowest_diversity_sample
                  ],
        }
        df_summary = pd.DataFrame(data)
        return df_summary
        
        
    
    


def create_quality_subplot(plot, experiment_name = "max_new"):
    if plot.is_test:
        pass
    else:
        plt.switch_backend("Qt5Agg")
    plt.close('all')
    x_data = ['cLNTX_bind', 'cLNTX_non-bind', 'cLNTX_+-', 'cLNTX_++', "aBGTX_+-", "aBGTX_++", "aBGTX_-+"]
    fig = plt.figure(figsize=(20, 26),  layout = "tight")
    plt.style.use("seaborn-v0_8-colorblind")
    plot.ControlFigure.stop_fig_update = True
    font_settings_title = {'fontfamily': 'serif', 'fontsize': '12', 'fontstyle': 'normal'}
    font_settings_normal = {'fontfamily': 'serif', 'fontsize': '10', 'fontstyle': 'normal'} 
    colorbar_settings = {'cmap': 'Blues', 'orientation': 'vertical', 'extend': 'neither', 'shrink': 0.8, 'pad': 0.05}
    gs = gridspec.GridSpec(2, 2, figure=fig,
                       )  # Adjusted to 5 rows

    # Rarefaction (spanning 2 rows)
    ax1 = fig.add_subplot(gs[1, 1])


    rarecurves = plots.rarefraction_curves.RarefractionCurves(plot.sequencing_report, 
                                                 plot.experiments_list,
                                                 plot.region_of_interest,
                                                 font_settings = font_settings_normal,
                                                 legend_settings = plot.legend_settings)


    cmap = plt.cm.Set2  # Choose any available colormap (e.g., viridis, plasma, inferno, magma)

    # Number of lines
    num_lines = len(rarecurves.plot_data)
    for i, row in rarecurves.plot_data.iterrows():
        color = cmap(i / num_lines)
        ax1.plot(
        row["x_axis"],
        row["y_axis"],
        label=row["samples"],
        alpha=1,
        fillstyle="full",
        linewidth=1.2,
        color = color
    )
    rarecurves.customize_axis(font_settings_normal)
    my_legend = plt.legend(plot.experiments_list, title="Sample Names", **plot.legend_settings)

    for text, new_label in zip(my_legend.get_texts(), x_data):
        text.set_text(new_label)
    title = "\n".join(wrap("Sequencing depth of the given samples", 40))
    ax1.set_xlabel("Tot. sampled sequences", **font_settings_normal)
    ax1.set_ylabel("Tot. unique sequences", **font_settings_normal)
 
    title = "\n".join(wrap(title, 40))
    ax1.set_title(title, pad=12, **font_settings_title)
    ax1.spines['right'].set_visible(False) 
    ax1.spines['top'].set_visible(False)
    

    # Alignment QQ (increased height by spanning 2 rows)
    if experiment_name is not None:
        import glob
        files = glob.glob(r"C:\Users\nilsh\my_projects\ExpoSeq\my_experiments\max_new\alignment_reports\*")
        report = load_alignment_reports(files)
        plot.alignment_report = report
        
    plot.alignment_report.head(10)
    if plot.alignment_report.columns.tolist() != []:
        ax2 = fig.add_subplot(gs[0, 0])
        data = plots.barplot.PrepareData().cleaning_data(plot.alignment_report, 
                                                  plot.sequencing_report)
        ax2.bar(
            data.Experiment,
            np.array(data.tot_sequenced_reads).astype(np.float32),
            label="Total sequenced reads",
            color="lightsalmon",
            alpha=1,
        )
        ax2.bar(
            data.Experiment,
            np.array(data.Aligned_Reads).astype(np.float32),
            label="Aligned reads",
            color="lightskyblue",
            alpha=1,
        )
        ax2.set_xticks(range(len(x_data)))  # Set the ticks to be at positions where you have data points
        ax2.set_xticklabels(x_data) 
        plt.xticks(rotation=45, ha="right", size=8)
 
        ax2.set_ylabel("Reads Count", **font_settings_normal)
        ax2.set_xlabel("Sample", **font_settings_normal)
        title = "\n".join(wrap("Alignment quality of the analyzed samples", 40))
        title = "\n".join(wrap(title, 40))
        ax2.set_title(title, pad=12, **font_settings_title)
        ax2.legend(**plot.legend_settings)
        ax2.spines['right'].set_visible(False) 
        ax2.spines['top'].set_visible(False)

    # Diversity (increased height by spanning 2 rows)
    ax3 = fig.add_subplot(gs[0, 1])
    Diversity = plots.diversity_plot.DiversityPlot(plot.sequencing_report,
                                       plot.region_of_interest,
                                        font_settings = font_settings_normal,
                                        )
    Diversity.ax = ax3
    values, unique_experiments = plots.diversity_plot.PrepareData().cleaning(
            plot.sequencing_report, plot.region_of_interest, Diversity.method
        )
    Diversity.create_base_plot(values, unique_experiments)

    ax3.set_ylabel("Inverse Simpson Index", **font_settings_normal)
    ax3.set_xlabel("Sample", **font_settings_normal)

    ax3.set_xticklabels(
            labels=plot.experiments_list, rotation=45, ha="right", size=8
        )
    ax3.set_xticks(range(len(x_data)))  # Set the ticks to be at positions where you have data points
    ax3.set_xticklabels(x_data) 
    title = "Diversity based on inverse Simpson index"
    title = "\n".join(wrap(title, 40))
    ax3.set_title(title, pad=12, **font_settings_title)
    ax3.spines['right'].set_visible(False) 
    ax3.spines['top'].set_visible(False)

    # Morosita Horn
    ax4 = fig.add_subplot(gs[1, 0])
    
    Matrix = plots.matrices.make_matrix.IdentityMatrix(plot.sequencing_report,
                                              plot.region_of_interest,
                                              matrix_type = "morosita_horn",
                                              colorbar_settings = plot.colorbar_settings,
                                              font_settings = font_settings_normal,
                                            
                                              )
    Matrix.ax = ax4
 #   Matrix.createPlot(colorbar_settings = colorbar_settings)
    annot_kws = {"size": 6}
    
    sns.heatmap(Matrix.matrix,
                                ax = ax4,
                                linewidths=0,
                                linecolor = "white",
                                annot = False,
                                annot_kws=annot_kws,
                                fmt = ".2f",
                                cmap= "Blues", 
                                cbar = False)
    fig.colorbar(cm.ScalarMappable(norm = Normalize(0, 1) ,cmap="Blues"), ax = ax4, use_gridspec=True, location='right', label='Degree of Identity' )

    plt.xticks(ticks = np.arange(0.5, len(plot.experiments_list) + 0.5 ,1),
        labels = plot.experiments_list,
        rotation = 45,
        ha = 'right',
        size = 8) # create a function which finds the perfect size based on counts of xlabels
    plt.yticks(ticks = np.arange(0.5, len(plot.experiments_list) + 0.5 ,1),
            labels = plot.experiments_list,
            rotation = 0,
            va='center',
            size=8)
    ax4.set_xticks(ticks = np.arange(0.5, len(plot.experiments_list) + 0.5 ,1),
                    labels = x_data,
        rotation = 45,
        ha = 'right',
        size = 8)  # Set the ticks to be at positions where you have data points
    ax4.set_xticklabels(x_data)  
    ax4.set_yticks(ticks = np.arange(0.5, len(plot.experiments_list) + 0.5 ,1),
            labels = x_data,
            rotation = 0,
            va='center',
            size=8)  # Set the ticks to be at positions where you have data points
    ax4.set_yticklabels(x_data)  
    ax4.set_xlabel("Sample", **font_settings_normal)
    ax4.set_ylabel("Sample", **font_settings_normal)
    title = "Identity between samples based on Morosita-Horn index"
    title = "\n".join(wrap(title, 40))
    ax4.set_title(title, pad=12, **font_settings_title)
    ax4.spines['right'].set_visible(False) 
    ax4.spines['top'].set_visible(False)

    # Summary
 #   ax5 = fig.add_subplot(gs[2:4, 1])
 #   ax5.axis('off')
 #   df_summary = SummarizeReport().create_summary(plot)
  #  table_data = df_summary.values
 #   table = ax5.table(cellText=table_data, colLabels=df_summary.columns, cellLoc='center', loc='center')
  #  table.auto_set_font_size(False)
  #  table.set_fontsize(12)
    #table.scale(1.2, 1.2)
    
        # Adjust cell heights
  #  cell_height = 0.1  # Example height, adjust based on your needs
  #  for key, cell in table.get_celld().items():
  #      cell.set_height(cell_height)
    # Loop through all cells, adjusting line visibility and color
 #   for key, cell in table.get_celld().items():
  #      cell.set_linewidth(0.8)  # Set the line width for visibility
  #      cell.set_edgecolor('black')  # Set edge color to black for visibility
  #      if key[0] == 0:  # For header cells
  #          cell.visible_edges = 'open'  # No horizontal lines for header if preferred
  #      else:
  #          cell.visible_edges = 'horizontal'  # Horizontal edges visible for all other rows

    # Manually set a thicker horizontal line between the header and the first row
 #   for i in range(len(df_summary.columns)):
  #      table[(0, i)].set_edgecolor('black')
   #     table[(1, i)].set_linewidth(2)  # Thick line after the header
   #     table[(1, i)].visible_edges = 'T'  # Only top edge visible


 #   gs.tight_layout(fig)
    #fig.set_size_inches(16, 10)  # Adjust the size as needed

    #fig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05, hspace=0.4, wspace=0.4)
    axes = [ax1, ax2, ax3, ax4]
    labels = ['d)', 'a)'  , 'b)','c)']
    for ax, label in zip(axes, labels):
        ax.text(-0.1, 1.1, label, transform=ax.transAxes, fontsize=12, va='top', ha='right', fontweight = "bold")

    
    fig.suptitle("Quality Assessment of the sequenced samples", fontsize=16, fontweight='bold')

    plt.savefig("subplot_quality_assessement.png", dpi = 300,  format = "png")
    
    plt.show()

from ExpoSeq.pipeline import PlotManager

plot = PlotManager(experiment = "max_new", test_version = True, no_automation=True,allow_binding_data=False, show_df=False)
create_quality_subplot(plot)
