import numpy as np
from keras.models import load_model
from keras.preprocessing import image # Convert the image to a numpy array
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# These are the  class labels from the training data (Each number stands for the currency denomination)
class_labels = [
    '10','100','20','200','2000','50','500','Background'
]
# Load model
my_new_model = load_model('static\style\model\Indian_Currency_model.h5')


def generate_plot(labels, values):
    # Replace this with your logic to get prediction data
    # labels = ['Class A', 'Class B', 'Class C']
    # values = [30, 50, 20]

    # Create a bar chart
    plt.switch_backend('agg')
    plt.bar(labels, values)
    plt.xlabel('Classes')
    plt.ylabel('Prediction Values')
    plt.title('Prediction Bar Chart')

    # Save the plot to a BytesIO object
    img_data = BytesIO()
    plt.savefig(img_data, format='png')
    img_data.seek(0)
    plt.close()

    # Encode the BytesIO object to base64
    encoded_img = base64.b64encode(img_data.getvalue()).decode('utf-8')

    return encoded_img

def prediction(file_name):
    img = image.load_img(file_name, target_size=(256,256))

    image_to_test = image.img_to_array(img)

    # Add a fourth dimension to the image (since Keras expects a list of images, not a single image)
    list_of_images = np.expand_dims(image_to_test, axis=0)

    # Make a prediction using the model
    results = my_new_model.predict(list_of_images)
    # print(f"results : {results}")
    # Since we are only testing one image, we only need to check the first result
    single_result = results[0]

    # Get the encoded image
    plot_data = generate_plot(class_labels, single_result)

    # We will get a likelihood score for all 10 possible classes. Find out which class had the highest score.
    most_likely_class_index = int(np.argmax(single_result))
    class_likelihood = single_result[most_likely_class_index]

    # Get the name of the most likely class
    class_label = class_labels[most_likely_class_index]

    # if no currency detected or uploaded image is  bagkground
    if(class_label=="Background"):
        mytext='Sorry but I am detecting only the '+class_label.lower()+', please hold the note under the camera.'
    else:
        mytext="This is Rs. {} note, and I am {: .2f} % sure of it.".format(class_label, class_likelihood*100)

    # Print the result
    # print(file_name)
    print("This is image is a {} - Likelihood: {:2f}".format(class_label, class_likelihood))

    return (class_label, class_likelihood, plot_data, mytext) 
