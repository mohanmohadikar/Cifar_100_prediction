# Copyright @ 2020 ABCOM Information Systems Pvt. Ltd. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

import os
import uuid
import flask
import urllib
from PIL import Image
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.applications.xception import Xception
import joblib
import pickle
from flask import Flask , render_template  , request , send_file
from tensorflow.keras.preprocessing.image import load_img , img_to_array

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#model = load_model(os.path.join(BASE_DIR , 'ModelWebApp.hdf5'))
model = load_model(os.path.join(BASE_DIR , 'cifar_100_cnn.h5'))
#model = load_model("static/model.h5")
#joblib_file = open("static/tokenizer.p", "rb")
# Load from file
#tokenizer = pickle.load(joblib_file)


ALLOWED_EXT = set(['jpg' , 'jpeg' , 'png' , 'jfif'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXT

#classes = ['airplane' ,'automobile', 'bird' , 'cat' , 'deer' ,'dog' ,'frog', 'horse' ,'ship' ,'truck']
classes = [
		'beaver', 'dolphin', 'otter', 'seal', 'whale',
		'aquarium fish', 'flatfish', 'ray', 'shark', 'trout',
		'orchids', 'poppies', 'roses', 'sunflowers', 'tulips',
		'bottles', 'bowls', 'cans', 'cups', 'plates',
		'apples', 'mushrooms', 'oranges', 'pears', 'sweet peppers',
		'clock', 'computer keyboard', 'lamp', 'telephone', 'television',
		'bed', 'chair', 'couch', 'table', 'wardrobe',
		'bee', 'beetle', 'butterfly', 'caterpillar', 'cockroach',
		'bear', 'leopard', 'lion', 'tiger', 'wolf',
		'bridge', 'castle', 'house', 'road', 'skyscraper',
		'cloud', 'forest', 'mountain', 'plain', 'sea',
		'camel', 'cattle', 'chimpanzee', 'elephant', 'kangaroo',
		'fox', 'porcupine', 'possum', 'raccoon', 'skunk',
		'crab', 'lobster', 'snail', 'spider', 'worm',
		'baby', 'boy', 'girl', 'man', 'woman',
		'crocodile', 'dinosaur', 'lizard', 'snake', 'turtle',
		'hamster', 'mouse', 'rabbit', 'shrew', 'squirrel',
		'maple', 'oak', 'palm', 'pine', 'willow',
		'bicycle', 'bus', 'motorcycle', 'pickup' 'truck', 'train',
		'lawn-mower', 'rocket', 'streetcar', 'tank', 'tractor'
		]


def predict(filename , model):
	img = load_img(filename , target_size = (32 , 32))
	img = img_to_array(img)
	img = img.reshape(1 , 32 ,32 ,3)

	img = img.astype('float32')
	img = img/255.0
	result = model.predict(img)

	dict_result = {}
	for i in range(10):
	    dict_result[result[0][i]] = classes[i]

	res = result[0]
	res.sort()
	res = res[::-1]
	prob = res[:3]
	
	prob_result = []
	class_result = []
	for i in range(3):
		prob_result.append((prob[i]*100).round(2))
		class_result.append(dict_result[prob[i]])

	return class_result , prob_result




@app.route('/')
def home():
	print("okkk")
	return render_template("index.html")

@app.route('/success' , methods = ['GET' , 'POST'])
def success():
	error = ''
	target_img = os.path.join(os.getcwd() , 'static/images')
	if request.method == 'POST':
		if(request.form):
			link = request.form.get('link')
			try :
				resource = urllib.request.urlopen(link)
				unique_filename = str(uuid.uuid4())
				filename = unique_filename+".jpg"
				img_path = os.path.join(target_img , filename)
				output = open(img_path , "wb")
				output.write(resource.read())
				output.close()
				img = filename

				res = pred(img_path)

				#class_result , prob_result = predict(img_path , model)

				predictions = {
					  "class1":res,
					    "class2":"class_result[1]",
					    "class3":"class_result[2]",
					    "prob1": "prob_result[0]",
					    "prob2": "prob_result[1]",
					    "prob3": "prob_result[2]",
				}

			except Exception as e : 
				print(str(e))
				error = 'This image from this site is not accesible or inappropriate input'

			if(len(error) == 0):
				return  render_template('success.html' , img  = img , predictions = predictions)
			else:
				return render_template('index.html' , error = error) 

			

		elif (request.files):
			file = request.files['file']
			if file and allowed_file(file.filename):
				file.save(os.path.join(target_img , file.filename))
				img_path = os.path.join(target_img , file.filename)
				img = file.filename
				res = pred(img_path)

				#class_result , prob_result = predict(img_path , model)
			#really nigga.
				predictions = {
					  "class1":res,
					    "class2":"class_result[1]",
					    "class3":"class_result[2]",
					    "prob1": "prob_result[0]",
					    "prob2": "prob_result[1]",
					    "prob3": "prob_result[2]",
				}

			else:
				error = "Please upload images of jpg , jpeg and png extension only"

			if(len(error) == 0):
				return  render_template('success.html' , img  = img , predictions = predictions)
			else:
				return render_template('index.html' , error = error)

	else:
		return render_template('index.html')




# load and prepare the image
def load_image(filename):
	# load the image
   img = filename.resize((32,32))
	# convert to array
   img = img_to_array(img)
	# reshape into a single sample with 3 channels
   img = img.reshape(1, 32, 32, 3)
	# prepare pixel data
   img = img.astype('float32')
   img = img / 255.0
   return img
 
# load an image and predict the class
def pred(img_file):
	# load the image
	img = load_image(img_file)
	# load model
	#model = load_model('final_model.h5')
	# predict the class
	result = model.predict_classes(img)
	return classes[result[0]-1]
 






if __name__ == "__main__":
	app.run(debug = True)


