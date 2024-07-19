import starbars
import matplotlib.pyplot as plt

# Example data with labels
categories = ['A', 'B', 'C', 'D']
values = [10, 30, 45, 5]
annotations = [('A', 'B', 0.05), ('A', 'C', 0.05), ('B', 'C', 0.01), ('A', 'D', 0.05), ('B', 'D', 0.01), ('D', 'C', 0.01)]
plt.bar(categories, values)

# Annotate significance
starbars.draw_annotation(annotations, ns_show=False)
plt.show()


# Example data with numbers
categories = [1, 2, 3]
values = [10, 20, 15]
annotations = [(2, 3, 0.01), (3, 1, 0.5)]
plt.bar(categories, values)

# Annotate significance
starbars.draw_annotation(annotations)
plt.show()