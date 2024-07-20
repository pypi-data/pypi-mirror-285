from setuptools import setup, Extension

setup(
    ext_modules=[
        Extension(
            name='read_sim',
            sources=["src/adnator/read_simulation.cpp"],
            extra_compile_args=['-O3', '-fopenmp', '-std=c++17'],
            extra_link_args=['-fopenmp']
        ),
    ]
)
