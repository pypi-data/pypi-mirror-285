import numpy as np
from sortedcontainers import SortedList

import libcasm.clexulator as casmclex
import libcasm.configuration as config
import libcasm.configuration.io.spglib as spglib_io

from .functions import check_symmetry_dataset


def test_configuration_constructor(simple_cubic_binary_prim):
    prim = config.Prim(simple_cubic_binary_prim)
    T = np.array(
        [
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
        ]
    )
    supercell = config.make_canonical_supercell(config.Supercell(prim, T))
    configuration = config.Configuration(supercell)
    assert type(configuration) == config.Configuration


def test_configuration_dof_values(simple_cubic_binary_prim):
    prim = config.Prim(simple_cubic_binary_prim)
    T = np.array(
        [
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
        ]
    )
    supercell = config.make_canonical_supercell(config.Supercell(prim, T))
    configuration = config.Configuration(supercell)
    dof_values = configuration.dof_values
    assert type(dof_values) == casmclex.ConfigDoFValues
    assert dof_values is configuration.dof_values

    assert configuration.occ(0) == 0
    configuration.dof_values.set_occupation([1])
    assert configuration.occ(0) == 1


def test_configuration_occupation(simple_cubic_binary_prim):
    prim = config.Prim(simple_cubic_binary_prim)
    T = np.array(
        [
            [4, 0, 0],
            [0, 4, 0],
            [0, 0, 4],
        ]
    )
    supercell = config.make_canonical_supercell(config.Supercell(prim, T))
    configuration = config.Configuration(supercell)

    occupation = configuration.occupation
    assert occupation.shape == (64,)
    assert configuration.occ(0) == 0
    assert (occupation == np.array([0] * 64)).all()

    configuration.set_occ(0, 1)
    occupation = configuration.occupation
    assert configuration.occ(0) == 1
    assert (occupation == np.array([1] + [0] * 63)).all()

    configuration.set_occupation([1, 1] + [0] * 62)
    assert (occupation == np.array([1, 1] + [0] * 62)).all()

    occupation = np.array([1] * 3 + [0] * 61, dtype=int)
    configuration.set_occupation(occupation)
    assert (configuration.occupation == np.array([1] * 3 + [0] * 61)).all()
    assert configuration.occupation.shape == (64,)


def test_canonical_configuration_occupation(simple_cubic_binary_prim):
    prim = config.Prim(simple_cubic_binary_prim)
    T = np.array(
        [
            [4, 0, 0],
            [0, 4, 0],
            [0, 0, 4],
        ]
    )
    supercell = config.make_canonical_supercell(config.Supercell(prim, T))
    configuration = config.Configuration(supercell)

    configuration.set_occ(0, 1)
    assert config.is_canonical_configuration(configuration) is True

    configuration.set_occ(0, 0)
    configuration.set_occ(10, 1)
    canon_config = config.make_canonical_configuration(configuration)
    assert config.is_canonical_configuration(canon_config) is True
    assert (canon_config.occupation == np.array([1] + [0] * 63)).all()


def test_configuration_invariant_subgroup(simple_cubic_binary_prim):
    prim = config.Prim(simple_cubic_binary_prim)
    T = np.array(
        [
            [4, 0, 0],
            [0, 4, 0],
            [0, 0, 4],
        ]
    )
    supercell = config.make_canonical_supercell(config.Supercell(prim, T))
    configuration = config.Configuration(supercell)

    invariant_subgroup = config.make_invariant_subgroup(configuration)
    assert len(invariant_subgroup) == 64 * 48

    configuration.set_occ(0, 1)
    invariant_subgroup = config.make_invariant_subgroup(configuration)
    assert len(invariant_subgroup) == 48


def test_configuration_spglib_io(simple_cubic_binary_prim):
    prim = config.Prim(simple_cubic_binary_prim)
    T = np.array(
        [
            [4, 0, 0],
            [0, 4, 0],
            [0, 0, 4],
        ]
    )
    supercell = config.make_canonical_supercell(config.Supercell(prim, T))
    configuration = config.Configuration(supercell)

    cell = spglib_io.as_cell(configuration)

    assert isinstance(cell, tuple)
    assert len(cell) == 3

    symmetry_dataset = spglib_io.get_symmetry_dataset(configuration)
    check_symmetry_dataset(symmetry_dataset, number=221, n_rotations=64 * 48)

    configuration.set_occ(0, 1)
    symmetry_dataset = spglib_io.get_symmetry_dataset(configuration)
    check_symmetry_dataset(symmetry_dataset, number=221, n_rotations=48)


def test_configuration_apply(simple_cubic_binary_prim):
    prim = config.Prim(simple_cubic_binary_prim)
    T = np.array(
        [
            [4, 0, 0],
            [0, 4, 0],
            [0, 0, 4],
        ]
    )
    supercell = config.make_canonical_supercell(config.Supercell(prim, T))
    configuration = config.Configuration(supercell)
    configuration.set_occ(l=0, s=1)
    configuration.set_occ(l=1, s=1)

    rep = config.SupercellSymOp.begin(supercell)
    end = config.SupercellSymOp.end(supercell)
    i = 0
    equivs = SortedList()
    while rep != end:
        transformed = rep * configuration
        if transformed not in equivs:
            equivs.add(transformed)
        rep.next()
        i += 1
    assert i == 48 * 64
    assert len(equivs) == 192


def test_copy_configuration(simple_cubic_binary_prim):
    import copy

    prim = config.Prim(simple_cubic_binary_prim)
    T = np.array(
        [
            [4, 0, 0],
            [0, 4, 0],
            [0, 0, 4],
        ]
    )
    supercell = config.make_canonical_supercell(config.Supercell(prim, T))
    configuration1 = config.Configuration(supercell)
    configuration2 = copy.copy(configuration1)
    configuration3 = copy.deepcopy(configuration1)

    assert isinstance(configuration1, config.Configuration)
    assert isinstance(configuration2, config.Configuration)
    assert isinstance(configuration3, config.Configuration)
    assert configuration2 is not configuration1
    assert configuration3 is not configuration1
