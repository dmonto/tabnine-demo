
@patch('image_generator.genai.GenerativeModel')
@patch('image_generator.Image.open')
@patch('image_generator.os.makedirs')
@patch('image_generator.datetime')
def test_generate_image_success_one_image(self, mock_datetime, mock_makedirs, mock_image_open, mock_generative_model):
    """
    Should successfully generate and save an image with a valid prompt and one input image.
    """
    # --- Arrange ---
    # Mock the API response to simulate receiving an image
    mock_api_response = MagicMock()
    mock_inline_data = MagicMock()
    mock_inline_data.mime_type = "image/png"
    # Create dummy image bytes
    dummy_image_bytes = BytesIO()
    Image.new('RGB', (10, 10)).save(dummy_image_bytes, format='PNG')
    mock_inline_data.data = dummy_image_bytes.getvalue()
    
    mock_part = MagicMock()
    # Configure the mock part to have 'inline_data'
    type(mock_part).inline_data = PropertyMock(return_value=mock_inline_data)
    # Make sure hasattr check passes
    mock_part.configure_mock(**{'inline_data.mime_type': "image/png"})

    mock_api_response.parts = [mock_part]
    
    # Mock the model and its generate_content method
    mock_model_instance = MagicMock()
    mock_model_instance.generate_content.return_value = mock_api_response
    mock_generative_model.return_value = mock_model_instance

    # Mock Image.open to return a mock image object that can be saved
    mock_pil_image = MagicMock()
    mock_image_open.return_value = mock_pil_image

    # Mock datetime to control the output filename
    mock_now = MagicMock()
    mock_now.strftime.return_value = "20230101_120000"
    mock_datetime.datetime.now.return_value = mock_now

    # Create a temporary file to act as the input image
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        input_image_path = tmp.name
    
    prompt = "A test prompt"
    expected_output_path = os.path.join("generated_images", "generated_20230101_120000.png")

    # --- Act ---
    result = generate_image(prompt, [input_image_path])

    # --- Assert ---
    self.assertEqual(result, expected_output_path)
    mock_makedirs.assert_called_once_with("generated_images", exist_ok=True)
    mock_generative_model.assert_called_once_with("gemini-2.5-flash-image-preview")
    # Check that Image.open was called for the input path
    mock_image_open.assert_any_call(input_image_path)
    # Check that generate_content was called with the correct prompt and image
    mock_model_instance.generate_content.assert_called_once()
    call_args = mock_model_instance.generate_content.call_args
    self.assertEqual(call_args.kwargs['contents'][0], prompt)
    self.assertIn(mock_pil_image, call_args.kwargs['contents'])
    # Check that the generated image was saved
    mock_pil_image.save.assert_called_once_with(expected_output_path, "PNG")

    # Cleanup the temporary file
    os.remove(input_image_path)
