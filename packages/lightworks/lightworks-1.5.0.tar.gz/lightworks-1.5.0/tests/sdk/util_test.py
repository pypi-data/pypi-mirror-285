# Copyright 2024 Aegiq Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from random import randint, random, seed

import pytest
from numpy import identity

from lightworks import (
    db_loss_to_transmission,
    random_permutation,
    random_unitary,
    transmission_to_db_loss,
)
from lightworks.sdk.utils import (
    add_heralds_to_state,
    add_mode_to_unitary,
    check_random_seed,
    check_unitary,
    permutation_mat_from_swaps_dict,
)


class TestUtils:
    """
    Unit tests to check functionality of various utilities included with the
    SDK.
    """

    def test_random_unitary(self):
        """
        Checks that when given a seed the random_unitary function always
        produces the same result. If this is not the case it would break many
        of the other unit tests.
        """
        unitary = random_unitary(4, seed=111)
        # Check one diagonal element and two off-diagonals
        assert unitary[0, 0] == pytest.approx(
            -0.49007982458868 + 0.212658840316704j, 1e-8
        )
        assert unitary[1, 2] == pytest.approx(
            -0.3483593186025 - 0.683182137239902j, 1e-8
        )
        assert unitary[3, 2] == pytest.approx(
            0.12574265147702 - 0.1257183128681681j, 1e-8
        )

    def test_random_permutation(self):
        """
        Checks that random permutation consistently returns the same results.
        """
        unitary = random_permutation(4, seed=44)
        # Check one diagonal element and two off-diagonals
        assert unitary[0, 0] == 0j
        assert unitary[0, 1] == 1 + 0j
        assert unitary[3, 0] == 0j

    def test_check_unitary(self):
        """Confirm that the check unitary function behaves as expected."""
        # Check both random unitary and identity matrix
        assert check_unitary(random_unitary(8))
        assert check_unitary(identity(8))
        assert check_unitary(identity(8, dtype=complex))

    def test_swaps_to_permutations(self):
        """
        Checks that conversion from swaps dict to permutation matrix works as
        expected.
        """
        swaps = {0: 2, 2: 3, 3: 1, 1: 0}
        unitary = permutation_mat_from_swaps_dict(swaps, 4)
        assert abs(unitary[2, 0]) ** 2 == 1
        assert abs(unitary[3, 1]) ** 2 == 0
        assert abs(unitary[3, 2]) ** 2 == 1

    def test_db_loss_to_decimal_conv(self):
        """Test conversion from db loss to a decimal transmission value."""
        r = db_loss_to_transmission(0.5)
        assert r == pytest.approx(0.8912509381337456, 1e-8)

    def test_decimal_to_db_loss_conv(self):
        """
        Tests conversion between a decimal transmission and db loss value.
        """
        r = transmission_to_db_loss(0.75)
        assert r == pytest.approx(1.2493873660829995, 1e-8)

    def test_seeded_random(self):
        """
        Checks that the result from the python random module remains consistent
        when using the same seed. If this changes then it could result in other
        unit tests failing.
        """
        seed(999)
        assert random() == pytest.approx(0.7813468849570298, 1e-8)

    @pytest.mark.parametrize("mode", [0, 3, 5, 6])
    def test_add_mode_to_unitary_value(self, mode):
        """
        Checks that add_mode_to_unitary function works correctly for a variety
        of positions, producinh .
        """
        unitary = random_unitary(6)
        new_unitary = add_mode_to_unitary(unitary, mode)
        # Check diagonal value on new mode
        assert new_unitary[mode, mode] == 1.0
        # Also confirm one off-diagonal value
        assert new_unitary[mode, mode - 1] == 0.0

    @pytest.mark.parametrize("mode", [0, 3, 5, 6])
    def test_add_mode_to_unitary_diagonal(self, mode):
        """
        Checks that add_mode_to_unitary function works correctly for a variety
        of positions.
        """
        unitary = random_unitary(6)
        new_unitary = add_mode_to_unitary(unitary, mode)
        # Confirm preservation of unitary on diagonal
        assert (new_unitary[:mode, :mode] == unitary[:mode, :mode]).all()
        assert (
            new_unitary[mode + 1 :, mode + 1 :] == unitary[mode:, mode:]
        ).all()

    @pytest.mark.parametrize("mode", [0, 3, 5, 6])
    def test_add_mode_to_unitary_off_diagonal(self, mode):
        """
        Checks that add_mode_to_unitary function works correctly for a variety
        of positions.
        """
        unitary = random_unitary(6)
        new_unitary = add_mode_to_unitary(unitary, mode)
        # Confirm preservation on unitary off diagonal
        assert (new_unitary[mode + 1 :, :mode] == unitary[mode:, :mode]).all()
        assert (new_unitary[:mode, mode + 1 :] == unitary[:mode, mode:]).all()

    def test_add_heralds_to_state(self):
        """
        Tests that add heralds to state generates the correct mode structure.
        """
        s = [1, 2, 3, 4, 5]
        heralds = {1: 6, 6: 7}
        s_new = add_heralds_to_state(s, heralds)
        assert s_new == [1, 6, 2, 3, 4, 5, 7]

    def test_add_heralds_to_state_unordered(self):
        """
        Tests that add heralds to state generates the correct mode structure,
        when the heralding dict is not ordered.
        """
        s = [1, 2, 3, 4, 5]
        heralds = {6: 7, 1: 6}
        s_new = add_heralds_to_state(s, heralds)
        assert s_new == [1, 6, 2, 3, 4, 5, 7]

    def test_add_heralds_to_state_empty_herald(self):
        """
        Tests that the original state is returned when no heralds are used.
        """
        s = [randint(0, 5) for i in range(10)]
        s_new = add_heralds_to_state(s, {})
        assert s == s_new

    def test_add_heralds_to_state_no_modification(self):
        """
        Checks that add heralds to state does not modify the original state.
        """
        s = [randint(0, 5) for i in range(10)]
        s_copy = list(s)  # Creates copy of list
        add_heralds_to_state(s, {6: 7, 1: 6})
        assert s == s_copy

    def test_add_heralds_to_state_new_object(self):
        """
        Confirms that a new object is still created when no heralds are used
        with a given state.
        """
        s = [randint(0, 5) for i in range(10)]
        s_new = add_heralds_to_state(s, {})
        assert id(s) != id(s_new)

    @pytest.mark.parametrize("value", [0.5, 3.2, "1.1", "seed", [1], (1,)])
    def test_check_random_seed(self, value):
        """
        Confirms that check_random_seed detects invalid seeds.
        """
        with pytest.raises(TypeError):
            check_random_seed(value)
