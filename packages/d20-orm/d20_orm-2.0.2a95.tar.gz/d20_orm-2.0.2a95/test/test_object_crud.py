# Create
version_parameter = Metadata.Parameter()
version_parameter.value = version
version_parameter.insert()

# Load by id
version = Metadata.Parameter()
version.load('CORE_VERSION_example')

# Load by value
version = Metadata.Parameter(data={'_key': 'CORE_VERSION'})
version.find()

# Update
version_parameter = Metadata.Parameter()
version_parameter.load('CORE_VERSION')
version_parameter.update()

# Delete
version_parameter = Metadata.Parameter()
version_parameter.load('CORE_VERSION')
version_parameter.delete()

