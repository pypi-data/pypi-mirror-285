def get_model_output(model) -> int:
    dummy_data = np.random.rand(1, 224, 224, 3)
    # Get prediction
    predictions = model.predict(dummy_data)

    # return the class output
    return np.argmax(predictions[0])


def test_code():
    main_method = "MyModel"
    input_shape = "input_shape"
    output_classes = "output_classes"

    def MyModel(input_shape=(224, 224, 3), output_classes=3):
        base_mobilenet_model = MobileNet(
            input_shape=input_shape, include_top=False, weights=None
        )
        multi_disease_model = Sequential()
        multi_disease_model.add(base_mobilenet_model)
        multi_disease_model.add(GlobalAveragePooling2D())
        multi_disease_model.add(Dropout(0.5))
        multi_disease_model.add(Dense(output_classes, activation="sigmoid"))
        return multi_disease_model


def get_model_info(model):
    # For Sequential model
    if isinstance(model, tf.keras.Sequential):
        # Get the input shape
        try:
            model_input_shape = model.input_shape[1:]
        except:
            raise ValueError(
                "Unable to determine input shape for the Sequential model."
            )

        # Get the number of output classes
        try:
            model_output_classes = model.layers[-1].units
        except:
            raise ValueError(
                "Unable to determine number of output classes for the Sequential model."
            )

    # For Functional model
    elif isinstance(model, tf.keras.Model):
        # Get the input shape
        try:
            model_input_shape = model.layers[0].input_shape[0][1:]
        except:
            raise ValueError(
                "Unable to determine input shape for the Functional model."
            )

        # Get the number of output classes
        try:
            output_shape = model.output_shape
            if len(output_shape) == 2:
                model_output_classes = output_shape[1]
            else:
                raise ValueError
        except:
            raise ValueError(
                "Unable to determine number of output classes for the Functional model."
            )

    else:
        raise ValueError("Model is neither Sequential nor Functional.")

    return model_input_shape, model_output_classes
