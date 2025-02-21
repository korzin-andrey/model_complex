import matplotlib.pyplot as plt


def recovered_plot(st_time, end_time, city, method, regim, save_path, model, time_step):
    if time_step == "week":
        res = model.get_weekly_recovered_by_group()
    else:
        res = model.get_daily_recovered_by_group()

    label = {0: "0-14 years", 1: "15+ years"} if len(res) == 2 else {0: "total"}
    color = {0: "blue", 1: "orange"}

    for i in range(len(res)):
        plt.plot(res[i], label=f"{label[i]}", color=color[i])

    plt.title(f"{method.capitalize()}, {regim.capitalize()}")
    plt.legend()

    plt.savefig(
        save_path + f"REC_{city}_{method}_{regim}_{st_time}_{end_time}.png", dpi=600
    )
    plt.savefig(
        save_path + f"REC_{city}_{method}_{regim}_{st_time}_{end_time}.pdf", dpi=600
    )
    plt.clf()
