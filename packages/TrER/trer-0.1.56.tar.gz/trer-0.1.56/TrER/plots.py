import matplotlib.pyplot as plt
from .utils import rearrange_cvar
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import numpy as np, pandas as pd

# markers = ["o", "^", "s", "d", "p"]  # Se asocia a cada Type
# colors = ["blue", "green", "red", "purple", "orange"]  # Se asocia a cada b
ggplot_c = ["#00BA38", "#F8766D", "#619CFF"]

def_ggplot_c = [
    "#F8766D",
    "#EA8331",
    "#D89000",
    "#C09B00",
    "#A3A500",
    "#7CAE00",
    "#39B600",
    "#00BB4E",
    "#00BF7D",
    "#00C1A3",
    "#00BFC4",
    "#00BAE0",
    "#00B0F6",
    "#35A2FF",
    "#9590FF",
    "#C77CFF",
    "#E76BF3",
    "#FA62DB",
    "#FF62BC",
    "#FF6A98",
]


def plot_cvar(
    data_ref,
    x="p",
    y="CVaR",
    zz=1.64485,
    cvar_se="CVaR_se",
    alpha=0.5,
    ylabel=r"${CVaR}_{\alpha}$",
    xlabel=r"$\alpha$",
    rearrangement=False,
):
    """
    Plots the Conditional Value at Risk (CVaR) with confidence intervals.

    Parameters:
    -----------
    data_ref : DataFrame
        The DataFrame containing the data to plot.
    x : str, optional
        The column name for the x-axis (default is "p").
    y : str, optional
        The column name for the y-axis (default is "CVaR").
    zz : float, optional
        The z-score multiplier for the confidence interval (default is 1.64485).
    cvar_se : str, optional
        The column name for the standard error of CVaR (default is "CVaR_se").
    alpha : float, optional
        The transparency level of the confidence interval ribbon (default is 0.5).
    ylabel : str, optional
        The label for the y-axis (default is r"${CVaR}_{\alpha}$").
    xlabel : str, optional
        The label for the x-axis (default is r"$\alpha$").
    rearrangement : bool, optional
        If True, applies rearrangement to the CVaR values (default is False).

    Returns:
    --------
    None

    Example:
    --------
    >>> plot_cvar(data, x='p', y='CVaR', cvar_se='CVaR_se')
    """
    # Calculate upper and lower bounds for the ribbon
    data = data_ref.copy()
    if rearrangement:
        data[y] = rearrange_cvar(data[y])
    data["ymin"] = data[y] - zz * data[cvar_se]
    data["ymax"] = data[y] + zz * data[cvar_se]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(data[x], data[y], marker="o", linestyle="-", color="b", label=y)
    plt.fill_between(
        data[x],
        data["ymin"],
        data["ymax"],
        alpha=alpha,
        color="b",
        label=f"{y} +/- {zz} * {cvar_se}",
    )
    plt.xlabel(xlabel, fontsize=14)
    plt.ylabel(ylabel, fontsize=14)
    plt.title("CVaR Plot", fontsize=16)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_CVAR_TE(
    data,
    ps,
    w_col="sw",
    y_col="Y",
    ipw_col="ipw",
    A_col="A",
    x_label=r"$\alpha$",
    y_label=r"CVaR",
    # color
):
    """
    Plots the Conditional Value at Risk Treatment Effect (CVaR TE) and confidence intervals.

    Parameters:
    -----------
    data : DataFrame
        The DataFrame containing the input data.
    ps : array-like
        Array of probabilities.
    w_col : str, optional
        The name of the column in the DataFrame that contains sample weights (default is "sw").
    y_col : str, optional
        The name of the column in the DataFrame that contains the outcome values (default is "Y").
    ipw_col : str, optional
        The name of the column in the DataFrame that contains inverse probability weights (default is "ipw").
    A_col : str, optional
        The name of the column in the DataFrame that contains the treatment indicator (default is "A").
    x_label : str, optional
        The label for the x-axis (default is r"$\alpha$").
    y_label : str, optional
        The label for the y-axis (default is "CVaR").

    Returns:
    --------
    None

    Example:
    --------
    >>> ps = np.linspace(0.1, 0.9, 9)
    >>> plot_CVAR_TE(data, ps, w_col='sw', y_col='Y', ipw_col='ipw', A_col='A')
    """
    sw_ipw_y = data[w_col] * data[y_col] * data[ipw_col]
    a_d = data[A_col]

    a_d1 = sw_ipw_y * a_d
    a_d0 = sw_ipw_y * (1 - a_d)
    s_n = np.sqrt(len(data))
    se1 = np.std(a_d1) / s_n
    se0 = np.std(a_d0) / s_n
    mu1 = np.mean(a_d1)
    mu0 = np.mean(a_d0)

    cvte = pd.DataFrame({"p": ps})

    cvte["se1"] = se1
    cvte["se0"] = se0
    cvte["mu1"] = mu1
    cvte["mu0"] = mu0

    df = cvte

    df["cvar1"] = np.where(
        df["p"] > 1 - df["mu1"], (df["mu1"] - (1 - df["p"])) / df["p"], 0
    )
    df["cvar1.se"] = np.where(df["p"] > 1 - df["mu1"], df["se1"] / df["p"], 0)
    df["cvar0"] = np.where(
        df["p"] > 1 - df["mu0"], (df["mu0"] - (1 - df["p"])) / df["p"], 0
    )
    df["cvar0.se"] = np.where(df["p"] > 1 - df["mu0"], df["se1"] / df["p"], 0)

    # Calcula cvar.te y cvar.te.se
    df["cvar.te"] = df["cvar1"] - df["cvar0"]
    df["cvar.te.se"] = np.sqrt(df["cvar1.se"] ** 2 + df["cvar0.se"] ** 2)

    df1 = df.copy()
    df2 = df.copy()
    df3 = df.copy()

    df1["Group"] = "A=1"
    df2["Group"] = "A=0"
    df3["Group"] = "diff"

    df1["cvar"] = df1["cvar1"]
    df2["cvar"] = df2["cvar0"]
    df3["cvar"] = df2["cvar.te"]

    df1["cvar_se"] = df1["cvar1.se"]
    df2["cvar_se"] = df2["cvar0.se"]
    df3["cvar_se"] = df2["cvar.te.se"]

    cols = ["cvar", "cvar_se", "Group", "p"]
    results = pd.concat((df1, df2, df3))[cols]
    zz = 1.64485
    results["ymin"] = results["cvar"] - zz * results["cvar_se"]
    results["ymax"] = results["cvar"] + zz * results["cvar_se"]

    combined_data = results.copy()

    fig, ax = plt.subplots()

    groups = combined_data["Group"].unique()
    colors = {"A=1": ggplot_c[0], "A=0": ggplot_c[1], "diff": ggplot_c[2]}

    for group in groups:
        group_data = combined_data[combined_data["Group"] == group]
        ax.plot(group_data["p"], group_data["cvar"], label=group, color=colors[group])
        ax.fill_between(
            group_data["p"],
            group_data["ymin"],
            group_data["ymax"],
            color=colors[group],
            alpha=0.5,
        )
        ax.scatter(group_data["p"], group_data["cvar"], color=colors[group], s=20)

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.legend(title="Group")
    plt.show()


def plot_cvar_group(
    data,
    x="p",
    y="CVaR",
    x_label=r"$\alpha$",
    y_label="CVaR",
    group="b",
    cvar_se="CVaR_se",
    zz=1.64,
    sx=7,
    lw=0.5,
    colors=None,
    rearrangement=True,
):
    """
    Plots grouped Conditional Value at Risk (CVaR) with confidence intervals.

    Parameters:
    -----------
    data : DataFrame
        The DataFrame containing the data to plot.
    x : str, optional
        The column name for the x-axis (default is "p").
    y : str, optional
        The column name for the y-axis (default is "CVaR").
    x_label : str, optional
        The label for the x-axis (default is r"$\alpha$").
    y_label : str, optional
        The label for the y-axis (default is "CVaR").
    group : str, optional
        The column name to group by (default is "b").
    cvar_se : str, optional
        The column name for the standard error of CVaR (default is "CVaR_se").
    zz : float, optional
        The z-score multiplier for the confidence interval (default is 1.64).
    sx : float, optional
        The size of markers in the scatter plot (default is 7).
    lw : float, optional
        The linewidth of the line plot (default is 0.5).
    colors : list of str, optional
        List of colors for plotting (default is a predefined list of colors).
    rearrangement : bool, optional
        If True, applies rearrangement to the CVaR values (default is True).

    Returns:
    --------
    None

    Example:
    --------
    >>> plot_cvar_group(data, x='p', y='CVaR', group='b')
    """

    if colors is None:
        colors = def_ggplot_c

    data[group] = np.round(data[group], 2)
    for i, (g, group_df) in enumerate(data.groupby(group)):
        if rearrangement:
            group_df = group_df.sort_values(x)
            group_df[y] = rearrange_cvar(group_df[y])
        group_df["ymin"] = group_df[y] - zz * group_df[cvar_se]
        group_df["ymax"] = group_df[y] + zz * group_df[cvar_se]

        plt.scatter(
            group_df[x],
            group_df[y],
            color=colors[i],
            s=sx,
            # label=f"{g} Scatter" if i == 0 else None  # Etiqueta solo en la primera iteración
        )
        plt.plot(
            group_df[x],
            group_df[y],
            color=colors[i],
            linewidth=lw,
            # label=f"{g} Line" if i == 0 else None  # Etiqueta solo en la primera iteración
        )
        plt.fill_between(
            group_df[x],
            group_df["ymin"],
            group_df["ymax"],
            alpha=0.4,
            color=colors[i],
            label=g,  # Etiqueta solo en la primera iteración
        )

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend(title=group)
    plt.show()


def plot_cvar_groups_with_markers(
    df,
    x="x",
    y="y",
    cvar_se="CVaR_se",
    x_label=r"$\alpha$",
    y_label=r"${CVaR}_{\alpha}-\bar{\tau}$",
    title_legend="Legend",
    zz=1.64,
    main_group="b",
    sub_group_m="Type",
    colors=def_ggplot_c,
    markers=[".", ",", "o", "v", "^", "<", ">", "1", "2", "3", "4", "s", "p", "*", "h"],
    sx=7,
    lw=0.5,
    sort=True,
):
    """
    Plots grouped Conditional Value at Risk (CVaR) with markers and lines for each subgroup.

    Parameters:
    -----------
    df : DataFrame
        The DataFrame containing the data to plot.
    x : str, optional
        The column name for the x-axis (default is "x").
    y : str, optional
        The column name for the y-axis (default is "y").
    cvar_se : str, optional
        The column name for the standard error of CVaR (default is "CVaR_se").
    x_label : str, optional
        The label for the x-axis (default is r"$\alpha$").
    y_label : str, optional
        The label for the y-axis (default is r"${CVaR}_{\alpha}-\bar{\tau}$").
    title_legend : str, optional
        The title for the legend (default is "Legend").
    zz : float, optional
        The z-score multiplier for the confidence interval (default is 1.64).
    main_group : str, optional
        The column name to group by for the main groups (default is "b").
    sub_group_m : str, optional
        The column name to subgroup within the main group (default is "Type").
    colors : list of str, optional
        List of colors for plotting (default is a predefined list of colors).
    markers : list of str, optional
        List of markers for plotting (default is a predefined list of markers).
    sx : float, optional
        The size of markers in the scatter plot (default is 7).
    lw : float, optional
        The linewidth of the line plot (default is 0.5).
    sort : bool, optional
        If True, sorts the data before plotting (default is True).

    Returns:
    --------
    None

    Example:
    --------
    >>> plot_cvar_groups_with_markers(df, x='x', y='y', main_group='b', sub_group_m='Type')
    """

    # Iterar sobre cada valor único de 'b'
    for i, (b_val, group) in enumerate(df.groupby(main_group)):
        # Iterar sobre cada valor único de 'Type' dentro de main_group
        for j, (type_val, subgroup) in enumerate(group.groupby(sub_group_m)):
            if sort:
                subgroup[y] = rearrange_cvar(subgroup[y])
            subgroup["ymin"] = subgroup[y] - zz * subgroup[cvar_se]
            subgroup["ymax"] = subgroup[y] + zz * subgroup[cvar_se]
            # Scatter plot para cada combinación main_group y sub_group_m
            c = colors[i]
            m = markers[j]
            plt.scatter(subgroup[x], subgroup[y], color=c, marker=m, s=sx)
            # Plot de línea para cada combinación main_group y sub_group_m
            plt.plot(
                subgroup[x],
                subgroup[y],
                color=c,
                linestyle="-",
                # marker=m
                linewidth=lw,
            )

            # Fill_between para cada combinación main_group y sub_group_m
            plt.fill_between(
                subgroup[x], subgroup["ymin"], subgroup["ymax"], color=c, alpha=0.1
            )

    # Configurar etiquetas y leyenda
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    # Crear entradas personalizadas para la leyenda de markers (b)
    legend_markers = [
        Line2D(
            [0],
            [0],
            marker=marker,
            color="w",
            markerfacecolor="black",
            markersize=10,
            label=f"{sub_group_m}={sg}",
        )
        for marker, sg in zip(markers, df[sub_group_m].unique())
    ]
    # Crear entradas personalizadas para la leyenda de colores (Type)
    legend_colors = [
        Patch(facecolor=colors[i], label=f"{main_group}={mg}")
        for i, mg in enumerate(df[main_group].unique())
    ]

    # Mostrar leyendas separadas
    plt.legend(
        handles=legend_markers + legend_colors,
        # loc="best",
        loc="center left",
        bbox_to_anchor=(1, 0.5),
        title=title_legend,
    )

    # Mostrar el gráfico
    plt.show()
