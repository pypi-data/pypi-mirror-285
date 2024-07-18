from .clients import config as cfg
from .errors import InvalidVersionKind, RAIInvalidVersionWarning
from packaging.version import Version

# A simple container for 2 version objects, a lower bound and an upper bound.
#
# Equivalent to a packaging SpecifierSet defined as ">={lower_bound}, <{upper_bound}", but
# has the benefit that we can check whether a version that is not contained by the set is
# lower than the lower bound or higher than the higher bound, which is important for error
# reporting.
def version_range(low:str, high:str) -> tuple[Version, Version]:
    return (Version(low), Version(high))

# A list of rel libraries that the current version of relationalai depends on, including the
# range of compatible versions.
DEPENDENCIES = [
    ('std', '24c1872c-de8a-5b12-7648-3d72f007a7a9', version_range('0.1.0', '0.2.0')),
    ('graphlib', '04cd9c07-16aa-4433-bdd7-adfdfaee317d', version_range('0.1.0', '0.2.0'))
]

#--------------------------------------------------
# Public API
#--------------------------------------------------

#
# Generate a Rel query that will lookup the versions of Rel libraries currently installed in
# the database.
#
def generate_query():
    return _generate_query(DEPENDENCIES)

#
# Using the response from the query above, verify that the versions of the Rel libraries
# found in the database are compatible with the current dependencies of this python library.
#
# This function will raise an exception if dependencies are not met.
#
def check_dependencies(response:str, platform:str, config:cfg.Config, model_name:str):
    return _compare_dependencies(
        DEPENDENCIES,
        _extract_library_versions(response.results),
        _extract_std_version(response.results),
        platform,
        config,
        model_name
    )


#--------------------------------------------------
# Implementation Details
#--------------------------------------------------

def _extract_std_version(results):
    for result in results:
        if result["relationId"].startswith("/:output/:std"):
            for (version,) in result["table"].itertuples(index=False):
                return version
    return None

def _extract_library_versions(results):
    libraries = {}
    for result in results:
        if result["relationId"].startswith("/:output/:static_lock"):
            for (name, uuid, version) in result["table"].itertuples(index=False):
                libraries[(name, uuid)] = version
    return libraries

def _compare_dependencies(expected, lock, std, platform:str, config:cfg.Config, model_name:str):

    if platform == "":
        platform = "snowflake"

    # database is pre-versioning
    if not lock and not std:
        RAIInvalidVersionWarning(
            kind=InvalidVersionKind.SchemaOutOfDate,
            expected=expected,
            lock=lock,
            platform=platform,
            config=config,
            model_name=model_name,
        )
        return
    # database has std but no lock, it is using a package manager
    if not lock and std:
        RAIInvalidVersionWarning(
            kind=InvalidVersionKind.LibraryOutOfDate,
            expected=expected,
            lock=lock,
            platform=platform,
            config=config,
            model_name=model_name,
        )
        return

    errors = []
    for (name, uuid, range) in expected:
        key = (name, uuid)
        # library is missing from the database
        if key not in lock:
            errors.append((InvalidVersionKind.SchemaOutOfDate, name, uuid))
        else:
            version = Version(lock[key])
            # Rel library version higher than upper bound, too new
            if version >= range[1]:
                errors.append((InvalidVersionKind.LibraryOutOfDate, name, uuid))

            # Rel library version lower than lower bound, too old
            if version < range[0]:
                errors.append((InvalidVersionKind.SchemaOutOfDate, name, uuid))

    if errors:
        if all(kind == InvalidVersionKind.LibraryOutOfDate for (kind, _, _) in errors):
            kind = InvalidVersionKind.LibraryOutOfDate
        elif all(kind == InvalidVersionKind.SchemaOutOfDate for (kind, _, _) in errors):
            kind = InvalidVersionKind.SchemaOutOfDate
        else:
            kind = InvalidVersionKind.Incompatible
        RAIInvalidVersionWarning(
            kind=kind,
            expected=expected,
            lock=lock,
            platform=platform,
            errors=errors,
            config=config,
            model_name=model_name,
        )


def _generate_query(dependencies):
    bindings = " ;\n            ".join(
        ["(\"%s\", \"%s\")" % (name, uuid) for name, uuid, range in dependencies]
    )
    return f'''
    @no_diagnostics(:UNDEFINED_IDENTIFIER)
    def output[:std]: {{ std::version }}

    @no_diagnostics(:TYPE_MISMATCH)
    def output(:static_lock, name, uuid, version):
        rel(:pkg, :std, :pkg, :project, :static_lock, name, uuid, version) and
        {{
            {bindings}
        }}(name, uuid)'''
