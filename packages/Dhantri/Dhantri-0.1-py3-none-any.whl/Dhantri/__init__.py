def main():
    total_classes = int(input("Enter the total number of classes: "))
    attended_classes = int(input("Enter the number of classes attended: "))

    attended_percentage = (attended_classes / total_classes) * 100

    print(f"Attended percentage: {attended_percentage:.2f}%")  # Using format method with 2 decimal places

    if attended_percentage >= 75:
        print("Student is allowed to sit in the exam.")
    else:
        print("Student is not allowed to sit in the exam.")

if __name__ == "__main__":
    main()
