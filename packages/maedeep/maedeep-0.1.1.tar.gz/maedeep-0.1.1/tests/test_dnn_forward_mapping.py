from maedeep.dnn import (_forwardmapping)

def test_articulatory_to_contour(articulatory_parameters):
    contours_out = _forwardmapping.articulatory_to_contour(articulatory_parameters,
                                                           output_type="contour")
    assert len(contours_out) == 1
    assert len(contours_out[0].contours) == 4
    
def test_articulatory_to_area(articulatory_parameters):
    area_function_out = _forwardmapping.articulatory_to_area(articulatory_parameters,
                                                             output_type="area_function")
    assert hasattr(area_function_out, "area")
    assert hasattr(area_function_out, "length")
    assert area_function_out.length.shape == (40, 1)
    
def test_articulatory_to_task(articulatory_parameters):
    tasks_out = _forwardmapping.articulatory_to_task(articulatory_parameters)
    assert tasks_out.shape == (7, 1)
    
# def test_articulatory_to_tf(articulatory_parameters):
#     tf_out, freq = _forwardmapping.articulatory_to_transfer_function(articulatory_parameters)
#     assert tf_out.shape == (len(freq), 1)
    
def test_articulatory_to_formants(articulatory_parameters):
    formants_out = _forwardmapping.articulatory_to_formant(articulatory_parameters)
    assert formants_out.shape == (4, 1)

def contour_to_formants(contours):
    formants_out = _forwardmapping.contour_to_formant(contours)
    assert formants_out.shape == (4, 1)

def task_to_formants(tasks):
    formants_out = _forwardmapping.task_to_formant(tasks)
    assert formants_out.shape == (4, 1)
    
# def test_contours_to_area(contours, model, area_function):
#     area_function_out = _forwardmapping.contour_to_area(contours, model)
#     assert hasattr(area_function_out, "area")
#     assert hasattr(area_function_out, "length")
#     assert area_function_out.length.shape == (40, 1)
#     assert (area_function_out.area == area_function.area).all()
    
# def test_contour_to_task(contours, coeff, tasks):
#     tasks_out = _forwardmapping.contour_to_task(contours, coeff)
#     assert tasks_out.shape == (7, 1)
#     assert (tasks_out == tasks).all()
    
# def test_contour_to_transfer_function(contours, model, transfer_function):
#     tf_out, freq = _forwardmapping.contour_to_transfer_function(contours, model)
#     assert tf_out.shape == (len(freq), 1)
#     assert (tf_out == transfer_function[0]).all()
    
# def test_contour_to_formants(contours, model, formants):
#     formants_out = _forwardmapping.contour_to_formant(contours, model)
#     assert formants_out.shape == (4, 1)
#     assert (formants_out == formants).all()
    
# def test_area_to_transfer_function(area_function, transfer_function):
#     tf_out, freq = _forwardmapping.area_to_transfer_function(area_function)
#     assert tf_out.shape == (len(freq), 1)
#     assert (tf_out == transfer_function[0]).all()
    
# def test_area_to_formants(area_function, formants):
#     formants_out = _forwardmapping.area_to_formant(area_function)
#     assert formants_out.shape == (4, 1)
#     assert (formants_out == formants).all()