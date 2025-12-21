# linear_regression_example.py
# Complete Linear Regression code in Python (Machine Learning)

import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score


def main():
    # 1. Create sample dataset
    # Example: Study hours (X) vs Marks (y)
    X = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9], dtype=float).reshape(-1, 1)
    y = np.array([35, 40, 50, 55, 60, 65, 70, 75, 80], dtype=float)

    # 2. Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # 3. Create Linear Regression model
    model = LinearRegression()

    # 4. Train (fit) the model on training data
    model.fit(X_train, y_train)

    # 5. View learned parameters
    slope = model.coef_[0]      # m
    intercept = model.intercept_  # c
    print("=== Model Parameters ===")
    print(f"Slope (coefficient m): {slope}")
    print(f"Intercept (c): {intercept}")
    print(f"Equation of line: y = {slope:.3f} * x + {intercept:.3f}")
    print()

    # 6. Make predictions on test set
    y_pred = model.predict(X_test)

    print("=== Test Data vs Predictions ===")
    for x_val, actual, pred in zip(X_test.flatten(), y_test, y_pred):
        print(f"Hours: {x_val:.1f} | Actual Marks: {actual:.1f} | Predicted: {pred:.2f}")
    print()

    # 7. Evaluate the model
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    print("=== Evaluation Metrics ===")
    print(f"Mean Squared Error (MSE): {mse:.3f}")
    print(f"R² Score: {r2:.3f}")
    print()

    # 8. Predict for a new value
    new_hours = float(input("Enter study hours to predict marks (e.g., 7.5): "))
    new_hours_array = np.array([[new_hours]])
    predicted_marks = model.predict(new_hours_array)[0]
    print(f"Predicted marks for {new_hours} hours of study: {predicted_marks:.2f}")

    # 9. Plot the data points and regression line
    plt.figure()
    # Scatter plot of original data
    plt.scatter(X, y, label="Actual Data Points")

    # Line for predicted values (using all X for a smooth line)
    x_line = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
    y_line = model.predict(x_line)
    plt.plot(x_line, y_line, label="Regression Line")

    plt.title("Linear Regression: Study Hours vs Marks")
    plt.xlabel("Study Hours")
    plt.ylabel("Marks")
    plt.legend()
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    main()

