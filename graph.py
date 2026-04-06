import matplotlib.pyplot as plt

quality = [100, 80, 60, 40, 20]
accuracy = [74.07, 62.96, 59.26, 59.26, 37.04]

plt.figure()

plt.plot(quality, accuracy, marker='o')

plt.xlabel("Quality Level")
plt.ylabel("Overall Accuracy (%)")
plt.title("Overall Accuracy vs Video Quality")

plt.savefig("quality_accuracy_graph.png")
plt.show()