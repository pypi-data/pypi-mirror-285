depends = ('ITKPyBase', 'ITKIOImageBase', )
templates = (  ('OpenJPHImageIO', 'itk::OpenJPHImageIO', 'itkOpenJPHImageIO', True),
  ('OpenJPHImageIOFactory', 'itk::OpenJPHImageIOFactory', 'itkOpenJPHImageIOFactory', True),
)
factories = (("ImageIO","OpenJPH"),)
