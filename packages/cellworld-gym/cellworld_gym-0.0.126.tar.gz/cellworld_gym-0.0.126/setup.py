from setuptools import setup

setup(name='cellworld_gym',
      description='OpenAI gym environments for cellworld experimental setup',
      url='https://github.com/germanespinosa/cellworld_gym',
      author='German Espinosa',
      author_email='germanespinosa@gmail.com',
      long_description=open('./cellworld_gym/README.md').read() + '\n---\n<small>Package created with Easy-pack</small>\n',
      long_description_content_type='text/markdown',
      packages=['cellworld_gym'],
      install_requires=['cellworld_game', 'cellworld_belief', 'gym'],
      license='MIT',
      include_package_data=True,
      version='0.0.126',
      zip_safe=False)
