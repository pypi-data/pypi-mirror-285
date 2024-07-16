import pandas as pd
import matplotlib.pyplot as plt
import subprocess as sp
import warnings
warnings.filterwarnings('ignore')
sp.call('wget -nc https://github.com/y-takefuji/pasero/raw/main/data.csv',shell=True)

# Load the data
df = pd.read_csv('data.csv')

# Combine 'Year' and 'Month' for X-axis
df['YearMonth'] = df['Year'].astype(str) + df['Month'].astype(str).str.zfill(2)  # zero padding for single digit months

# Convert 'YearMonth' to datetime format for proper sorting
df['YearMonth'] = pd.to_datetime(df['YearMonth'], format='%Y%m')

# Get unique 'Pathogen' values
pathogens = df['Pathogen'].unique()
print("Pathogens:")
for i, pathogen in enumerate(pathogens):
    print(f"{i+1}. {pathogen}")

# User selects a pathogen
pathogen_choice = int(input("Select a pathogen by number: "))
selected_pathogen = pathogens[pathogen_choice - 1]

# Get unique 'Serotype/Species/Subgroup' values for the selected pathogen
serotypes = df[df['Pathogen'] == selected_pathogen]['Serotype/Species/Subgroup'].unique()
print("\nSerotypes:")
for i, serotype in enumerate(serotypes):
    print(f"{i+1}. {serotype}")

# User selects up to 4 serotypes
serotype_choices = list(map(int, input("Select up to 4 serotypes by number (separated by space): ").split()))
selected_serotypes = [serotypes[i - 1] for i in serotype_choices]

# Set line styles and widths
styles = ['-', '-', ':', ':', '--', '--', '-.', '-.']
widths = [1, 2, 1, 2, 1, 2, 1, 2]

# User selects Y-axis values
print("\n1. Number of isolates\n2. Past two years average and % Change")
y_choice = int(input("Select one by number: "))

# Plot the data
fig, ax = plt.subplots()
lines = []
labels = []
i = 0
for serotype in selected_serotypes:
    data = df[(df['Pathogen'] == selected_pathogen) & (df['Serotype/Species/Subgroup'] == serotype)]
    data = data.sort_values('YearMonth')
    if y_choice == 1:
        line, = ax.plot(data['YearMonth'], data['Number of isolates'], linestyle=styles[i], linewidth=widths[i], color='black')
        ax.set_ylabel('Number of isolates')
    else:
        line, = ax.plot(data['YearMonth'], data['Past two years average'], linestyle=styles[i], linewidth=widths[i], color='black')
        ax.set_ylabel('% Change')
        ax_right = ax.twinx()
        line_right, = ax_right.plot(data['YearMonth'], data['% Change'], linestyle=styles[(i+1)%8], linewidth=widths[(i+1)%8], color='black')            
        ax_right.set_ylabel('Baseline: Past two years average', rotation=270, labelpad=15)
        lines.append(line_right)
        labels.append(serotype+' change')
    lines.append(line)
    labels.append(serotype+' avg')
    i += 1

# Add legends
fig.legend(lines, labels, loc='upper right')

# Rotate X-axis labels using label function
labels = ax.get_xticklabels()
for label in labels:
    label.set_rotation(90)

# Format the filename
filename = selected_pathogen + '_' + '_'.join(selected_serotypes)
filename = filename.replace(':', '-')  # replace ':' with '-'
filename = filename.replace('/', '_')  # replace '/' with '_'
# Save the figure and data
def main():
 df.to_csv(f"{filename}.csv", index=False)
 plt.savefig(f"{filename}.png",dpi=300)

# Show the plot
 plt.show()

if __name__ == "__main__":
 main()
