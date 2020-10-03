# USAGE
# python crowd_counting.py --input pedestrians.mp4
# python crowd_counting.py --input pedestrians.mp4 --output output.avi

# import the necessary packages
from pyimagesearch import count_config as config
from pyimagesearch.detection import detect_people
import argparse
import imutils
import cv2
import os

projectDir = os.path.dirname(os.path.realpath(__file__))

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", type=str, default="",
	help="path to (optional) input video file")
ap.add_argument("-o", "--output", type=str, default="",
	help="path to (optional) output video file")
ap.add_argument("-d", "--display", type=int, default=1,
	help="whether or not output frame should be displayed")
args = vars(ap.parse_args())

# load the COCO class labels our YOLO model was trained on
#labelsPath = os.path.sep.join([config.MODEL_PATH, "coco.names"])
labelsPath = projectDir + "/yolo-coco/coco.names"
LABELS = open(labelsPath).read().strip().split("\n")

# derive the paths to the YOLO weights and model configuration
#weightsPath = os.path.sep.join([config.MODEL_PATH, "yolov3.weights"])
#configPath = os.path.sep.join([config.MODEL_PATH, "yolov3.cfg"])
weightsPath = projectDir + "/yolo-coco/yolov3.weights"
configPath = projectDir + "/yolo-coco/yolov3.cfg"


# load our YOLO object detector trained on COCO dataset (80 classes)
print("[INFO] loading YOLO from disk...")
net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)

# check if we are going to use GPU
if config.USE_GPU:
	# set CUDA as the preferable backend and target
	print("[INFO] setting preferable backend and target to CUDA...")
	net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
	net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

# determine only the *output* layer names that we need from YOLO
ln = net.getLayerNames()
ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]

# initialize the video stream and pointer to output video file
print("[INFO] accessing video stream...")
vs = cv2.VideoCapture(args["input"] if args["input"] else 0)
writer = None

# set up the variable for counting people file exporting
current_frame = 0
ppl_count_temp = 0
data_arr = []
period = 10
framerate = vs.get(cv2.CAP_PROP_FPS)

# For demo 10 mins clip represent 300 mins
# mod_no = (peroid * 60 * framerate) / 30

mod_no = (period * 60 * framerate)


# loop over the frames from the video stream
while True:

	# read the next frame from the file
	(grabbed, frame) = vs.read()

	# if the frame was not grabbed, then we have reached the end
	# of the stream
	if not grabbed:
		break

	# resize the frame and then detect people (and only people) in it
	frame = imutils.resize(frame, width=700)
	results = detect_people(frame, net, ln,
		personIdx=LABELS.index("person"))

	# loop over the results
	for (i, (prob, bbox, centroid)) in enumerate(results):
		# extract the bounding box and centroid coordinates, then
		# initialize the color of the annotation
		(startX, startY, endX, endY) = bbox
		(cX, cY) = centroid
		color = (0, 255, 0)


		# draw (1) a bounding box around the person and (2) the
		# centroid coordinates of the person,
		cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)
		cv2.circle(frame, (cX, cY), 5, color, 1)

	# draw the total number of social distancing violations on the
	# output frame
	text = "Crowd amount: {}".format(len(results))
	cv2.putText(frame, text, (10, frame.shape[0] - 25),
		cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 0, 255), 3)

	################# data gathering and export part #######################

	# increase frame counting
	current_frame += 1

	# get the people no in frame for finding the average
	ppl_count_temp += len(results)

	# find the average every 10 minutes
	# mod_no is no of frames in 10 mins
	if (current_frame % mod_no) == 0:
		data_arr.append(int(ppl_count_temp / mod_no))
		print(data_arr)
		ppl_count_temp = 0

	########################################################################

	# check to see if the output frame should be displayed to our
	# screen
	if args["display"] > 0:
		# show the output frame
		cv2.imshow("Frame", frame)
		key = cv2.waitKey(1)

		# if the `q` key was pressed, break from the loop
		if key == ord("q"):
			break

	# if an output video file path has been supplied and the video
	# writer has not been initialized, do so now
	if args["output"] != "" and writer is None:
		# initialize our video writer
		fourcc = cv2.VideoWriter_fourcc(*"MJPG")
		writer = cv2.VideoWriter(args["output"], fourcc, 25,
			(frame.shape[1], frame.shape[0]), True)

	# if the video writer is not None, write the frame to the output
	# video file
	if writer is not None:
		writer.write(frame)

#export txt file

filename = args["input"]

#remove video file
vidDir = projectDir.replace("/main", "")
vidDir = vidDir + '/media/videos'
os.remove(filename)

filename = filename.replace("Footages/", "")
filename = filename.replace(".m4v", "")
filename = filename.replace(".mp4", "")
temp = projectDir.replace("/main", "")
temp = temp + "/media/videos"
filename = filename.replace(temp, "")

print(filename)
print(projectDir)

with open(projectDir + '/txt/' + filename, 'w') as filehandle:
	for listitem in data_arr:
		filehandle.write('%s\n' % listitem)
	print("======= "+ filename +" is exported =======")