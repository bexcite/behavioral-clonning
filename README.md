# behavioral-clonning
Self-Driving Car Udacity project for behavioral cloning exploration and learning to predict a steering angle on the simulated environment.

## Making video from dataset

```
python video.py --dataset dataset/folder/ --output movie.mp4

python video.py --dataset ../../../sdc/behavioral-cloning/train2-complete

```




## TODO:

+ video.py - make video from --dataset folder to --output file (or 'movie.mp4' by default)
+ extract model.py (free it from junk) (linear & cnn model)
+ make model_train.py - training routine with saving etc.
+ train for overfitting model (linear & cnn) - DEBUG mode
+ clean dataset
- generate reverse dataset
- generate recovery dataset

python video.py --dataset ../../../sdc/behavioral-cloning/train2-complete

python train_model.py --dataset ../../../sdc/behavioral-cloning/train2-complete
