from tensorflow import keras
from keras.applications.resnet50 import ResNet50
from keras.applications.xception import Xception
from keras.applications.mobilenet import MobileNet
from keras.applications.mobilenet_v2 import MobileNetV2

from keras.utils import image_dataset_from_directory
from tensorflow import data as tf_data

def model_factory(model_name, image_shape, num_classes):
    include_top=False
    weights=None
    input_tensor=None
    input_shape=image_shape + (3,)
    pooling="avg"

    inputs = keras.Input(shape=input_shape)

    if model_name == "resnet50":
        base_model = ResNet50(weights=weights, include_top=include_top, pooling=pooling, input_tensor=input_tensor, input_shape=input_shape)
    elif model_name == "xception":
        base_model= Xception(weights=weights, include_top=include_top, pooling=pooling, input_tensor=input_tensor, input_shape=input_shape)
    elif model_name == "mobilenet":
        base_model= MobileNet(weights=weights, include_top=include_top, pooling=pooling, input_tensor=input_tensor, input_shape=input_shape)
    elif model_name == "mobilenetv2":
        base_model= MobileNetV2(weights=weights, include_top=include_top, pooling=pooling, input_tensor=input_tensor, input_shape=input_shape)
        
    x = base_model(inputs, training=False)
    
    outputs = keras.layers.Dense(num_classes, activation="softmax")(x)

    return keras.Model(inputs, outputs)



def add_layers(model):
    pass

def get_training_data(input_dir, image_shape, batch_size, classes, seed):
    train_ds, val_ds = image_dataset_from_directory(
        input_dir,
        validation_split=0.2,
        subset="both",
        seed=seed,
        image_size=image_shape,
        batch_size=batch_size,
        label_mode="categorical",
        labels="inferred",
        class_names=classes,
    )
       
        # Prefetching samples in GPU memory helps maximize GPU utilization.
    train_ds = train_ds.prefetch(tf_data.AUTOTUNE)
    val_ds = val_ds.prefetch(tf_data.AUTOTUNE)

    return train_ds, val_ds


def train_image_classifier(model_name, train_data_dir, image_shape, batch_size, classes, seed, epochs):

    train_ds, val_ds = get_training_data(train_data_dir, image_shape, batch_size, classes, seed)

    model = model_factory(model_name, image_shape, len(classes))
    model.summary(show_trainable=True)
    model.compile(
        optimizer=keras.optimizers.Adam(3e-4),
        loss=keras.losses.CategoricalCrossentropy(),
        metrics=[keras.metrics.CategoricalAccuracy(name="accuracy")],
    )

    print("Fitting " + model_name)
    model.fit(
        train_ds,
        epochs=epochs,
        validation_data=val_ds,
    )