from setuptools import setup

REQUIREMENTS = [
    'intervaltree == 3.1.0', 
    'docker == 6.0.1',
    'whisper @ git+https://github.com/openai/whisper.git'
]

if __name__ == "__main__":
    setup(name='gentle_whisper',
          version='0.1.0',
          description='',
          url='',
          author='Will Crichton',
          author_email='crichton.will@gmail.com',
          license='MIT',
          install_requires=REQUIREMENTS,
          packages=['gentle_whisper'],
          zip_safe=False)
