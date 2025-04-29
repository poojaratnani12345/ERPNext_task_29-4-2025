frappe.ui.form.on("Discussion Channel", {
    refresh(frm) {
        initializeRoleUsersMapping(frm);
        handleRoleChanges(frm);
    },

    role(frm) {
        handleRoleChanges(frm);
    },
});

function initializeRoleUsersMapping(frm) {
    if (!frm.doc.role_users_mapping) {
        frm.set_value("role_users_mapping", "{}");
    }
}

function handleRoleChanges(frm) {
    const selectedRoles = (frm.doc.role || []).map(r => r.role);
    const roleUsersMapping = JSON.parse(frm.doc.role_users_mapping || "{}");

    const previousRoles = Object.keys(roleUsersMapping);
    const removedRoles = previousRoles.filter(role => !selectedRoles.includes(role));

    if (removedRoles.length) {
        removedRoles.forEach(role => {
            const usersToRemove = roleUsersMapping[role] || [];
            frm.doc.members = frm.doc.members.filter(member => !usersToRemove.includes(member.user));
            delete roleUsersMapping[role];
        });
        frm.refresh_field("members");
        frm.set_value("role_users_mapping", JSON.stringify(roleUsersMapping));
    }

    if (selectedRoles.length) {
        updateMembersBasedOnRoles(frm, selectedRoles, roleUsersMapping);
    } else {
        removeRoleBasedUsers(frm);
    }
}

function updateMembersBasedOnRoles(frm, selectedRoles, existingMapping = {}) {
    frappe.call({
        method: "sarvadhi_custom.api.discussion.get_users_by_role",
        args: { roles: selectedRoles },
        callback({ message: users }) {
            if (!Array.isArray(users)) {
                frappe.msgprint("Invalid response received while fetching users.");
                return;
            }

            const existingUsers = new Set((frm.doc.members || []).map(m => m.user));

            selectedRoles.forEach(role => {
                const roleUsers = users.map(u => u.name);
                existingMapping[role] = roleUsers;

                roleUsers.forEach(userName => {
                    if (!existingUsers.has(userName)) {
                        const user = users.find(u => u.name === userName);
                        frm.add_child("members", {
                            user: userName,
                            username: user?.username || ""
                        });
                        existingUsers.add(userName);
                    }
                });
            });

            frm.refresh_field("members");
            frm.set_value("role_users_mapping", JSON.stringify(existingMapping));
        },
        error() {
            frappe.msgprint("An error occurred while fetching users.");
        }
    });
}

function removeRoleBasedUsers(frm) {
    const mapping = JSON.parse(frm.doc.role_users_mapping || "{}");
    const usersToRemove = Object.values(mapping).flat();

    frm.doc.members = (frm.doc.members || []).filter(member => !usersToRemove.includes(member.user));
    frm.refresh_field("members");
    frm.set_value("role_users_mapping", "{}");
}
